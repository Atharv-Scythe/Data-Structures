/**
 * Smart EV Charging Queue & Route Optimizer
 * Graph & Dijkstra Visualizer (SVG-based)
 */

class GraphVisualizer {
    constructor(svgElementId, infoElementId) {
        this.svg = document.getElementById(svgElementId);
        this.infoPanel = document.getElementById(infoElementId);
        this.vertices = [];
        this.edges = [];
        this.stations = [];
        this.nodePositions = {
            'A': { x: 100, y: 140 },
            'B': { x: 300, y: 80 },
            'C': { x: 220, y: 260 },
            'D': { x: 440, y: 240 },
            'E': { x: 580, y: 120 },
            'F': { x: 700, y: 260 }
        };
        this.highlightedPath = [];
        this.animatingEV = null;
    }

    setNodePositions(vertices) {
        // Assign circular layout for extra nodes if not in default map
        const count = vertices.length;
        const width = this.svg.clientWidth || 700;
        const height = this.svg.clientHeight || 340;
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) * 0.35;

        vertices.forEach((v, index) => {
            if (!this.nodePositions[v]) {
                const angle = (2 * Math.PI * index) / count;
                this.nodePositions[v] = {
                    x: Math.round(centerX + radius * Math.cos(angle)),
                    y: Math.round(centerY + radius * Math.sin(angle))
                };
            }
        });
    }

    render(graphData, stationData = [], activeRoute = null) {
        if (!this.svg) return;
        this.vertices = graphData.vertices || [];
        this.edges = graphData.edges || [];
        this.stations = stationData || [];
        if (activeRoute) {
            this.highlightedPath = activeRoute.path || [];
        }

        this.setNodePositions(this.vertices);

        // Deduplicate undirected edges for drawing
        const uniqueEdges = [];
        const seenEdgeKeys = new Set();

        this.edges.forEach(edge => {
            const src = edge.source;
            const dest = edge.destination;
            const key = [src, dest].sort().join("---");
            if (!seenEdgeKeys.has(key)) {
                seenEdgeKeys.add(key);
                uniqueEdges.push(edge);
            }
        });

        // Build SVG HTML
        let svgContent = `<defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <linearGradient id="edgeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#49d6a9" />
                <stop offset="100%" stop-color="#57a8ff" />
            </linearGradient>
        </defs>`;

        const isLight = document.documentElement.getAttribute("data-theme") === "light";

        // Render Edges
        uniqueEdges.forEach(edge => {
            const p1 = this.nodePositions[edge.source];
            const p2 = this.nodePositions[edge.destination];
            if (!p1 || !p2) return;

            const isHighlighted = this.isEdgeInPath(edge.source, edge.destination);
            const lineClass = isHighlighted ? "graph-edge highlighted" : "graph-edge";
            const strokeColor = isHighlighted ? (isLight ? "#059669" : "#49d6a9") : (isLight ? "#cbd5e1" : "#20344d");
            const strokeWidth = isHighlighted ? "4" : "2";
            const badgeBg = isLight ? "#ffffff" : "#0d1929";
            const badgeStroke = isHighlighted ? (isLight ? "#059669" : "#49d6a9") : (isLight ? "#cbd5e1" : "#20344d");
            const badgeText = isHighlighted ? (isLight ? "#059669" : "#49d6a9") : (isLight ? "#475569" : "#8ea3ba");

            svgContent += `
                <g class="edge-group">
                    <line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}"
                          class="${lineClass}" stroke="${strokeColor}" stroke-width="${strokeWidth}"
                          ${isHighlighted ? 'filter="url(#glow)"' : ''} />
                    <!-- Edge Weight Badge -->
                    <circle cx="${(p1.x + p2.x) / 2}" cy="${(p1.y + p2.y) / 2}" r="11" fill="${badgeBg}" stroke="${badgeStroke}" stroke-width="1.5" />
                    <text x="${(p1.x + p2.x) / 2}" y="${(p1.y + p2.y) / 2 + 4}"
                          class="edge-label" text-anchor="middle" fill="${badgeText}" font-size="10" font-weight="bold">
                        ${edge.weight}
                    </text>
                </g>
            `;
        });

        // Render Nodes
        this.vertices.forEach(v => {
            const pos = this.nodePositions[v];
            if (!pos) return;

            const isHighlightedNode = this.highlightedPath.includes(v);
            const isStart = this.highlightedPath.length > 0 && this.highlightedPath[0] === v;
            const isEnd = this.highlightedPath.length > 0 && this.highlightedPath[this.highlightedPath.length - 1] === v;
            const stationAtNode = this.stations.find(s => s.location === v);

            let nodeFill = isLight ? "#ffffff" : "#0d1929";
            let nodeStroke = isLight ? "#94a3b8" : "#20344d";
            let textColor = isLight ? "#0f172a" : "#edf5ff";

            if (isStart) {
                nodeFill = isLight ? "#d1fae5" : "#123b32";
                nodeStroke = isLight ? "#059669" : "#49d6a9";
                textColor = isLight ? "#065f46" : "#edf5ff";
            } else if (isEnd) {
                nodeFill = isLight ? "#dbeafe" : "#1a3454";
                nodeStroke = isLight ? "#2563eb" : "#57a8ff";
                textColor = isLight ? "#1e40af" : "#edf5ff";
            } else if (isHighlightedNode) {
                nodeFill = isLight ? "#ecfdf5" : "#16283d";
                nodeStroke = isLight ? "#059669" : "#49d6a9";
                textColor = isLight ? "#065f46" : "#edf5ff";
            }

            const haloColor = isLight ? "rgba(5, 150, 105, 0.18)" : "rgba(73, 214, 169, 0.18)";
            const stationBg = isLight ? "#f8fafc" : "#07111f";
            const stationAccent = isLight ? "#059669" : "#49d6a9";

            svgContent += `
                <g class="node-group" data-vertex="${v}" cursor="pointer">
                    <!-- Glow effect for start/end/path -->
                    ${isHighlightedNode ? `<circle cx="${pos.x}" cy="${pos.y}" r="26" fill="${haloColor}" />` : ''}
                    <circle cx="${pos.x}" cy="${pos.y}" r="20" fill="${nodeFill}" stroke="${nodeStroke}" stroke-width="${isHighlightedNode ? '3' : '2'}" />
                    <text x="${pos.x}" y="${pos.y + 5}" text-anchor="middle" fill="${textColor}" font-size="14" font-weight="bold">${v}</text>
                    
                    ${stationAtNode ? `
                        <g transform="translate(${pos.x + 12}, ${pos.y - 20})">
                            <rect width="24" height="16" rx="4" fill="${stationBg}" stroke="${stationAccent}" stroke-width="1.5" />
                            <text x="12" y="12" text-anchor="middle" fill="${stationAccent}" font-size="9" font-weight="bold">⚡${stationAtNode.station_id}</text>
                        </g>
                    ` : ''}
                </g>
            `;
        });

        // Render Animated EV if moving
        if (this.animatingEV) {
            svgContent += `
                <g id="animatedEVGroup" transform="translate(${this.animatingEV.x}, ${this.animatingEV.y})">
                    <circle r="14" fill="#49d6a9" filter="url(#glow)"/>
                    <text y="4" text-anchor="middle" fill="#07111f" font-size="10" font-weight="bold">🚗</text>
                </g>
            `;
        }

        this.svg.innerHTML = svgContent;
        this.updateInfoPanel(activeRoute);
    }

    isEdgeInPath(u, v) {
        if (!this.highlightedPath || this.highlightedPath.length < 2) return false;
        for (let i = 0; i < this.highlightedPath.length - 1; i++) {
            const p1 = this.highlightedPath[i];
            const p2 = this.highlightedPath[i + 1];
            if ((p1 === u && p2 === v) || (p1 === v && p2 === u)) {
                return true;
            }
        }
        return false;
    }

    updateInfoPanel(activeRoute) {
        if (!this.infoPanel) return;
        if (!activeRoute || !activeRoute.path || activeRoute.path.length === 0) {
            this.infoPanel.innerHTML = `
                <div class="route-info-empty">
                    <span>Algorithm: <strong>Dijkstra Shortest Path</strong></span>
                    <p class="muted-text">Select Start and Destination locations to calculate optimal route.</p>
                </div>
            `;
            return;
        }

        const pathStr = activeRoute.path.join(" ➔ ");
        this.infoPanel.innerHTML = `
            <div class="route-info-card">
                <div class="route-info-header">
                    <span class="badge-dijkstra">ALGORITHM: DIJKSTRA (Min-Heap Priority Queue)</span>
                    <span class="route-distance">Total Distance: <strong>${activeRoute.distance} units</strong></span>
                </div>
                <div class="route-path-display">
                    <span class="label">Shortest Path:</span>
                    <span class="path-sequence">${pathStr}</span>
                </div>
            </div>
        `;
    }

    async animateEVAlongPath(path, durationPerSegment = 800) {
        if (!path || path.length < 2) return;
        
        for (let i = 0; i < path.length - 1; i++) {
            const fromPos = this.nodePositions[path[i]];
            const toPos = this.nodePositions[path[i + 1]];
            if (!fromPos || !toPos) continue;

            const startTime = performance.now();

            await new Promise(resolve => {
                const step = (now) => {
                    const elapsed = now - startTime;
                    const progress = Math.min(1, elapsed / durationPerSegment);
                    
                    // Ease in-out
                    const ease = progress < 0.5 
                        ? 2 * progress * progress 
                        : 1 - Math.pow(-2 * progress + 2, 2) / 2;

                    this.animatingEV = {
                        x: fromPos.x + (toPos.x - fromPos.x) * ease,
                        y: fromPos.y + (toPos.y - fromPos.y) * ease
                    };
                    
                    // Re-render current frame
                    this.render({ vertices: this.vertices, edges: this.edges }, this.stations, { path: this.highlightedPath });

                    if (progress < 1) {
                        requestAnimationFrame(step);
                    } else {
                        resolve();
                    }
                };
                requestAnimationFrame(step);
            });
        }
        
        this.animatingEV = null;
        this.render({ vertices: this.vertices, edges: this.edges }, this.stations, { path: this.highlightedPath });
    }
}
