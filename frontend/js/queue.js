/**
 * Smart EV Charging Queue & Route Optimizer
 * Simple Queue Visualizer (FIFO)
 */

class QueueVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(items = []) {
        if (!this.container) return;

        if (!items.length) {
            this.container.className = "queue-container empty-state";
            this.container.innerHTML = `<div>Normal FIFO Queue is empty</div>`;
            return;
        }

        this.container.className = "queue-container";
        let html = `
            <div class="queue-header-meta">
                <span class="queue-size-badge">SIZE: <strong>${items.length}</strong></span>
                <span class="queue-peek-badge">NEXT OUT (FRONT): <strong>${this.escapeHTML(items[0].ev_id)}</strong></span>
            </div>
            <div class="queue-items-horizontal">
        `;

        items.forEach((ev, index) => {
            const isFront = index === 0;
            const isRear = index === items.length - 1;

            html += `
                <div class="queue-card ${isFront ? 'front-card' : ''} ${isRear ? 'rear-card' : ''}">
                    ${isFront ? '<span class="end-badge front">FRONT (Head)</span>' : ''}
                    ${isRear ? '<span class="end-badge rear">REAR (Tail)</span>' : ''}
                    
                    <div class="queue-card-body">
                        <div class="ev-card-id">${this.escapeHTML(ev.ev_id)}</div>
                        <div class="ev-card-meta">
                            <span>Pos: #${index + 1}</span>
                            <span>⚡ ${ev.battery_level}%</span>
                            <span>📍 ${this.escapeHTML(ev.location)}</span>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        this.container.innerHTML = html;
    }

    escapeHTML(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;");
    }
}
