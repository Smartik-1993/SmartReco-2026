/**
 * Non-blocking Event Tracker for SmartReco
 * Batches behavioral events and sends them via navigator.sendBeacon
 */
class SmartRecoTracker {
  constructor(batchSize = 5, flushIntervalMs = 4000) {
    this.queue = [];
    this.batchSize = batchSize;
    this.flushIntervalMs = flushIntervalMs;
    this.pageStartTime = Date.now();
    
    this.initListeners();
    this.startPeriodicFlush();
  }

  // Track arbitrary event
  track(eventType, payload = {}) {
    const event = {
      event_type: eventType,
      payload: JSON.stringify({
        ...payload,
        url: window.location.pathname,
        referrer: document.referrer,
        timestamp: new Date().toISOString()
      })
    };
    this.queue.push(event);

    if (this.queue.length >= this.batchSize) {
      this.flush();
    }
  }

  // Automatically flush remaining events on page exit or tab switch
  initListeners() {
    // Track dwell time before leaving page
    window.addEventListener('beforeunload', () => {
      const dwellTimeSec = Math.round((Date.now() - this.pageStartTime) / 1000);
      this.track('dwell_time', { duration_seconds: dwellTimeSec });
      this.flush();
    });

    // Flush on visibility state changes
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.flush();
      }
    });
  }

  startPeriodicFlush() {
    setInterval(() => this.flush(), this.flushIntervalMs);
  }

  // Primary non-blocking flush routine using Blob and sendBeacon
  flush() {
    if (this.queue.length === 0) return;

    const payload = JSON.stringify({ events: [...this.queue] });
    this.queue = []; // Clear queue immediately to avoid double sends

    // Use sendBeacon for zero-latency background execution
    if (navigator.sendBeacon) {
      const blob = new Blob([payload], { type: 'application/json' });
      const success = navigator.sendBeacon('/api/v1/events/batch', blob);
      if (!success) {
        // Fallback to fetch if sendBeacon buffer is full
        this.fallbackFetch(payload);
      }
    } else {
      this.fallbackFetch(payload);
    }
  }

  fallbackFetch(payload) {
    fetch('/api/v1/events/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payload,
      keepalive: true
    }).catch(err => console.error('Tracker flush error:', err));
  }
}

// Initialize global instance
window.smartRecoTracker = new SmartRecoTracker();

// Utility helpers for inline page tracking
function trackPageView(productId = null, category = null) {
  window.smartRecoTracker.track('page_view', { product_id: productId, category: category });
}

function trackSearch(searchQuery) {
  if (searchQuery.trim()) {
    window.smartRecoTracker.track('search', { query: searchQuery });
  }
}

function trackClick(productId, productName) {
  window.smartRecoTracker.track('product_click', { product_id: productId, title: productName });
}