// app/static/js/tracker.js
class EventTracker {
  constructor() {
    this.queue = [];
    this.batchInterval = 3000; // Send events every 3 seconds
    this.init();
  }

  init() {
    // Start background flusher
    setInterval(() => this.flush(), this.batchInterval);

    // Track search submissions
    document.addEventListener("DOMContentLoaded", () => {
      const searchForm = document.getElementById("search-form");
      if (searchForm) {
        searchForm.addEventListener("submit", (e) => {
          const input = document.getElementById("search-input");
          if (input && input.value) {
            this.track("search", { query: input.value });
          }
        });
      }

      // Track item clicks
      document.querySelectorAll("[data-track-click]").forEach((el) => {
        el.addEventListener("click", () => {
          this.track("click", {
            item_id: el.dataset.itemId,
            item_title: el.dataset.itemTitle,
          });
        });
      });
    });
  }

  track(eventType, payload) {
    this.queue.push({
      event_type: eventType,
      payload: JSON.stringify(payload),
    });
    console.log(`[Tracker] Enqueued: ${eventType}`, payload);
  }

  async flush() {
    if (this.queue.length === 0) return;

    const eventsToSend = [...this.queue];
    this.queue = [];

    try {
      const response = await fetch("/api/v1/events/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ events: eventsToSend }),
      });

      if (!response.ok) {
        // If request failed, push events back into queue
        this.queue.push(...eventsToSend);
      } else {
        console.log(`[Tracker] Flushed ${eventsToSend.length} event(s)`);
      }
    } catch (err) {
      console.warn("[Tracker] Flush failed, retry queued", err);
      this.queue.push(...eventsToSend);
    }
  }
}

const tracker = new EventTracker();