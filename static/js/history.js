
async function loadTripHistory() {
  const grid = document.querySelector("#historyGrid");
  const count = document.querySelector("#historyCount");
  const empty = document.querySelector("#historyEmpty");

  if (!grid || !count || !empty) {
    console.error("History page elements were not found.");
    return;
  }

  count.textContent = "Loading your trips...";
  grid.innerHTML = "";

  try {
    const trips = await api("/api/trip-history");

    count.textContent =
      `${trips.length} saved ${
        trips.length === 1 ? "itinerary" : "itineraries"
      }`;

    grid.innerHTML = trips.map((trip) => {
      const date = trip.created_at
        ? new Date(trip.created_at).toLocaleDateString("en-IN")
        : "Date unavailable";

      return `
        <article class="destination-card">
          <div class="destination-card-body">

            <p class="eyebrow">SAVED ITINERARY</p>

            <h3>${escapeHtml(trip.title || "My India trip")}</h3>

            <p class="muted">
              Created ${escapeHtml(date)}
            </p>

            <div class="plan-metrics">
              <div class="plan-metric">
                <span>Budget</span>
                <strong>${money(trip.budget)}</strong>
              </div>

              <div class="plan-metric">
                <span>Entrance fees</span>
                <strong>${money(trip.total_fee)}</strong>
              </div>

              <div class="plan-metric">
                <span>Visit time</span>
                <strong>${Number(trip.total_hours || 0)} h</strong>
              </div>
            </div>

            <p>
              Available time:
              ${Number(trip.hours_available || 0)} hours
            </p>

            <div class="history-actions">
              <button
                type="button"
                class="button button-primary"
                data-view-trip="${trip.id}">
                View itinerary ↗
              </button>

              <button
                type="button"
                class="button button-secondary"
                data-edit-trip="${trip.id}">
                Edit trip ✎
              </button>

              <button
                type="button"
                class="button button-secondary"
                data-delete-trip="${trip.id}">
                Delete trip 🗑
              </button>
            </div>

            <!-- Saved attraction details -->
            <div id="trip-details-${trip.id}" hidden></div>

            <!-- Edit itinerary form -->
            <div id="edit-trip-${trip.id}" hidden>
              <form data-trip-form="${trip.id}">

                <label>
                  Trip title
                  <input
                    name="title"
                    type="text"
                    value="${escapeHtml(trip.title || "My India trip")}"
                    required>
                </label>

                <label>
                  Budget (₹)
                  <input
                    name="budget"
                    type="number"
                    min="0"
                    step="0.01"
                    value="${Number(trip.budget || 0)}"
                    required>
                </label>

                <label>
                  Available hours
                  <input
                    name="hours_available"
                    type="number"
                    min="0.1"
                    step="0.1"
                    value="${Number(trip.hours_available || 0)}"
                    required>
                </label>

                <button
                  type="submit"
                  class="button button-primary">
                  Save changes
                </button>

              </form>
            </div>

          </div>
        </article>
      `;
    }).join("");

    empty.hidden = trips.length !== 0;
    grid.hidden = trips.length === 0;

  } catch (error) {
    count.textContent = "Unable to load saved itineraries.";

    grid.innerHTML = `
      <p class="error-message">
        ${escapeHtml(error.message || "Could not load your trips.")}
      </p>
    `;

    grid.hidden = false;
    empty.hidden = true;

    console.error("Failed to load trip history:", error);
  }
}


// Handle Edit, Delete, and View buttons.
document.addEventListener("click", async (event) => {

  // EDIT BUTTON
  const editButton = event.target.closest("[data-edit-trip]");

  if (editButton) {
    const tripId = editButton.dataset.editTrip;
    const editForm = document.querySelector(`#edit-trip-${tripId}`);

    if (editForm) {
      editForm.hidden = !editForm.hidden;

      editButton.textContent = editForm.hidden
        ? "Edit trip ✎"
        : "Cancel edit";
    }

    return;
  }

  // DELETE BUTTON
  const deleteButton = event.target.closest("[data-delete-trip]");

  if (deleteButton) {
    const tripId = deleteButton.dataset.deleteTrip;

    if (!confirm("Are you sure you want to delete this itinerary?")) {
      return;
    }

    deleteButton.disabled = true;
    deleteButton.textContent = "Deleting...";

    try {
      await api(`/api/trip-history/${tripId}`, {
        method: "DELETE"
      });

      toast("Itinerary deleted successfully!");
      await loadTripHistory();

    } catch (error) {
      toast(error.message || "Could not delete itinerary.");
      console.error("Delete failed:", error);

      deleteButton.disabled = false;
      deleteButton.textContent = "Delete trip 🗑";
    }

    return;
  }

  // VIEW BUTTON
  const viewButton = event.target.closest("[data-view-trip]");

  if (!viewButton) return;

  const tripId = viewButton.dataset.viewTrip;
  const details = document.querySelector(`#trip-details-${tripId}`);

  if (!details) return;

  if (!details.hidden) {
    details.hidden = true;
    viewButton.textContent = "View itinerary ↗";
    return;
  }

  viewButton.disabled = true;
  viewButton.textContent = "Loading...";

  try {
    const trip = await api(`/api/trip-history/${tripId}`);
    const items = trip.items || [];

    details.innerHTML = `
      <h3>Attractions in this itinerary</h3>

      ${
        items.length
          ? items.map((item, index) => `
              <article class="plan-item">

                <span class="plan-item-num">
                  ${String(index + 1).padStart(2, "0")}
                </span>

                <div>
                  <h4>
                    ${escapeHtml(item.name || "Unnamed attraction")}
                  </h4>

                  <p>
                    ${escapeHtml(
                      [item.city, item.state]
                        .filter(Boolean)
                        .join(" · ")
                    )}
                    <br>
                    ${Number(item.visit_hours || 0)} hours
                  </p>
                </div>

                <span class="plan-fee">
                  ${money(item.entrance_fee)}
                </span>

              </article>
            `).join("")
          : "<p>No attraction details were saved for this trip.</p>"
      }
    `;

    details.hidden = false;
    viewButton.textContent = "Hide itinerary ↑";

  } catch (error) {
    toast(error.message || "Could not load this itinerary.");
    console.error("Failed to load itinerary details:", error);

  } finally {
    viewButton.disabled = false;

    if (details.hidden) {
      viewButton.textContent = "View itinerary ↗";
    }
  }
});


// Save edited itinerary details.
document.addEventListener("submit", async (event) => {
  const form = event.target.closest("[data-trip-form]");

  if (!form) return;

  event.preventDefault();

  const tripId = form.dataset.tripForm;
  const formData = new FormData(form);

  const data = {
    title: String(formData.get("title") || "").trim(),
    budget: Number(formData.get("budget")),
    hours_available: Number(formData.get("hours_available"))
  };

  if (
    !data.title ||
    !Number.isFinite(data.budget) ||
    !Number.isFinite(data.hours_available) ||
    data.budget < 0 ||
    data.hours_available <= 0
  ) {
    toast("Please enter a valid title, budget, and available hours.");
    return;
  }

  const submitButton = form.querySelector('button[type="submit"]');

  submitButton.disabled = true;
  submitButton.textContent = "Saving...";

  try {
    await api(`/api/trip-history/${tripId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    toast("Itinerary updated successfully!");
    await loadTripHistory();

  } catch (error) {
    toast(error.message || "Could not update itinerary.");
    console.error("Failed to update itinerary:", error);

  } finally {
    if (form.isConnected) {
      submitButton.disabled = false;
      submitButton.textContent = "Save changes";
    }
  }
});


// Load saved trips when the page opens.
loadTripHistory();
