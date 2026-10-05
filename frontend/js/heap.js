/**
 * Smart EV Charging Queue & Route Optimizer
 * Min-Heap / Priority Queue Visualizer
 */

class HeapVisualizer {
    constructor(treeContainerId, arrayContainerId) {
        this.treeContainer = document.getElementById(treeContainerId);
        this.arrayContainer = document.getElementById(arrayContainerId);
        this.items = [];
    }

    render(heapItems = []) {
        this.items = heapItems || [];
        this.renderArrayView();
        this.renderTreeView();
    }

    renderArrayView() {
        if (!this.arrayContainer) return;
        if (!this.items.length) {
            this.arrayContainer.innerHTML = `<div class="empty-state">Priority Queue is empty</div>`;
            return;
        }

        let html = `<div class="heap-array-grid">`;
        this.items.forEach((item, idx) => {
            const isRoot = idx === 0;
            html += `
                <div class="heap-array-cell ${isRoot ? 'root-cell' : ''}">
                    <span class="cell-idx">[${idx}]</span>
                    <span class="cell-id">${this.escapeHTML(item.ev_id)}</span>
                    <span class="cell-priority">Priority: ${item.priority}</span>
                    ${isRoot ? '<span class="min-tag">MIN ROOT</span>' : ''}
                </div>
            `;
        });
        html += `</div>`;
        this.arrayContainer.innerHTML = html;
    }

    renderTreeView() {
        if (!this.treeContainer) return;
        if (!this.items.length) {
            this.treeContainer.innerHTML = `<div class="empty-state">Tree is empty</div>`;
            return;
        }

        // Calculate binary tree positions
        const levels = Math.floor(Math.log2(this.items.length)) + 1;
        const width = Math.max(340, Math.pow(2, levels - 1) * 70);
        const height = levels * 65 + 30;

        let svgHtml = `<svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow: visible;">
            <defs>
                <filter id="heapGlow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>`;

        const nodeCoords = [];

        // First pass: compute positions
        for (let i = 0; i < this.items.length; i++) {
            const level = Math.floor(Math.log2(i + 1));
            const levelIndex = i - (Math.pow(2, level) - 1);
            const numNodesInLevel = Math.pow(2, level);
            const segmentWidth = width / numNodesInLevel;
            const x = segmentWidth * levelIndex + segmentWidth / 2;
            const y = level * 65 + 40;
            nodeCoords.push({ x, y });
        }

        const isLight = document.documentElement.getAttribute("data-theme") === "light";
        const lineStroke = isLight ? "#cbd5e1" : "#20344d";

        // Draw parent-child connecting lines
        for (let i = 0; i < this.items.length; i++) {
            const leftChild = 2 * i + 1;
            const rightChild = 2 * i + 2;
            const pCoord = nodeCoords[i];

            if (leftChild < this.items.length) {
                const lCoord = nodeCoords[leftChild];
                svgHtml += `<line x1="${pCoord.x}" y1="${pCoord.y}" x2="${lCoord.x}" y2="${lCoord.y}" stroke="${lineStroke}" stroke-width="2" />`;
            }
            if (rightChild < this.items.length) {
                const rCoord = nodeCoords[rightChild];
                svgHtml += `<line x1="${pCoord.x}" y1="${pCoord.y}" x2="${rCoord.x}" y2="${rCoord.y}" stroke="${lineStroke}" stroke-width="2" />`;
            }
        }

        // Draw nodes
        for (let i = 0; i < this.items.length; i++) {
            const item = this.items[i];
            const coord = nodeCoords[i];
            const isMinRoot = i === 0;

            const fill = isMinRoot 
                ? (isLight ? "#d1fae5" : "#1b3a32") 
                : (isLight ? "#ffffff" : "#0d1929");
            const stroke = isMinRoot 
                ? (isLight ? "#059669" : "#49d6a9") 
                : (isLight ? "#94a3b8" : "#20344d");
            const textFill = isLight ? "#0f172a" : "#edf5ff";
            const priorityFill = isMinRoot 
                ? (isLight ? "#059669" : "#49d6a9") 
                : (isLight ? "#d97706" : "#ffc857");
            const haloFill = isLight ? "rgba(5, 150, 105, 0.18)" : "rgba(73, 214, 169, 0.2)";

            svgHtml += `
                <g class="heap-tree-node ${isMinRoot ? 'min-root' : ''}">
                    ${isMinRoot ? `<circle cx="${coord.x}" cy="${coord.y}" r="24" fill="${haloFill}" />` : ''}
                    <circle cx="${coord.x}" cy="${coord.y}" r="18" fill="${fill}" stroke="${stroke}" stroke-width="${isMinRoot ? '3' : '2'}" ${isMinRoot ? 'filter="url(#heapGlow)"' : ''} />
                    <text x="${coord.x}" y="${coord.y - 2}" text-anchor="middle" fill="${textFill}" font-size="10" font-weight="bold">${this.escapeHTML(item.ev_id)}</text>
                    <text x="${coord.x}" y="${coord.y + 10}" text-anchor="middle" fill="${priorityFill}" font-size="8" font-weight="bold">P:${item.priority}</text>
                </g>
            `;
        }

        svgHtml += `</svg>`;
        this.treeContainer.innerHTML = svgHtml;
    }

    escapeHTML(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;");
    }
}
