/**
 * ComfyUI GeomPack - Dual Mesh VTK.js Preview Widget
 * Shows two meshes with different colors for comparison
 */

import { app } from "../../../scripts/app.js";

console.log("[GeomPack] Loading VTK.js dual mesh preview extension...");

app.registerExtension({
    name: "geompack.meshpreview.vtk.dual",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "GeomPackPreviewMeshVTKDual") {
            console.log("[GeomPack] Registering Preview Mesh (VTK Dual) node");

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                console.log("[GeomPack VTK Dual] Node created, adding widget");

                // Create container for viewer + info panel
                const container = document.createElement("div");
                container.style.width = "100%";
                container.style.height = "100%";
                container.style.display = "flex";
                container.style.flexDirection = "column";
                container.style.backgroundColor = "#2a2a2a";
                container.style.overflow = "hidden";

                // Create iframe for VTK.js viewer (use textured viewer for GLB support)
                const iframe = document.createElement("iframe");
                iframe.style.width = "100%";
                iframe.style.flex = "1 1 0";
                iframe.style.minHeight = "0";
                iframe.style.border = "none";
                iframe.style.backgroundColor = "#2a2a2a";

                // Use textured viewer for GLB with vertex colors
                iframe.src = "/extensions/ComfyUI-GeometryPack/viewer_vtk_textured.html?v=" + Date.now();

                // Create mesh info panel (larger for two meshes)
                const infoPanel = document.createElement("div");
                infoPanel.style.backgroundColor = "#1a1a1a";
                infoPanel.style.borderTop = "1px solid #444";
                infoPanel.style.padding = "8px 12px";
                infoPanel.style.fontSize = "10px";
                infoPanel.style.fontFamily = "monospace";
                infoPanel.style.color = "#ccc";
                infoPanel.style.lineHeight = "1.4";
                infoPanel.style.flexShrink = "0";
                infoPanel.style.overflow = "auto";
                infoPanel.style.maxHeight = "200px";
                infoPanel.innerHTML = '<span style="color: #888;">Dual mesh info will appear here after execution</span>';

                // Add iframe and info panel to container
                container.appendChild(iframe);
                container.appendChild(infoPanel);

                // Add widget
                const widget = this.addDOMWidget("preview_vtk_dual", "MESH_PREVIEW_VTK_DUAL", container, {
                    getValue() { return ""; },
                    setValue(v) { }
                });

                widget.computeSize = () => [512, 700];  // Larger height for dual mesh info

                // Store references
                this.meshViewerIframeVTKDual = iframe;
                this.meshInfoPanelVTKDual = infoPanel;

                // Track iframe load state
                let iframeLoaded = false;
                iframe.addEventListener('load', () => {
                    console.log("[GeomPack VTK Dual] Iframe loaded");
                    iframeLoaded = true;
                });

                // Listen for messages from iframe
                window.addEventListener('message', async (event) => {
                    if (event.data.type === 'SCREENSHOT' && event.data.image) {
                        console.log('[GeomPack VTK Dual] Received screenshot');
                        // Screenshot handling (same as regular VTK viewer)
                        try {
                            const base64Data = event.data.image.split(',')[1];
                            const byteString = atob(base64Data);
                            const arrayBuffer = new ArrayBuffer(byteString.length);
                            const uint8Array = new Uint8Array(arrayBuffer);

                            for (let i = 0; i < byteString.length; i++) {
                                uint8Array[i] = byteString.charCodeAt(i);
                            }

                            const blob = new Blob([uint8Array], { type: 'image/png' });
                            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
                            const filename = `vtk-dual-screenshot-${timestamp}.png`;

                            const formData = new FormData();
                            formData.append('image', blob, filename);
                            formData.append('type', 'output');
                            formData.append('subfolder', '');

                            const response = await fetch('/upload/image', {
                                method: 'POST',
                                body: formData
                            });

                            if (response.ok) {
                                const result = await response.json();
                                console.log('[GeomPack VTK Dual] Screenshot saved:', result.name);
                            }
                        } catch (error) {
                            console.error('[GeomPack VTK Dual] Error saving screenshot:', error);
                        }
                    }
                    else if (event.data.type === 'MESH_ERROR' && event.data.error) {
                        console.error('[GeomPack VTK Dual] Error from viewer:', event.data.error);
                        if (infoPanel) {
                            infoPanel.innerHTML = `<div style="color: #ff6b6b; padding: 8px;">Error: ${event.data.error}</div>`;
                        }
                    }
                });

                // Set initial node size
                this.setSize([512, 700]);

                // Handle execution
                const onExecuted = this.onExecuted;
                this.onExecuted = function(message) {
                    console.log("[GeomPack VTK Dual] onExecuted called with message:", message);
                    onExecuted?.apply(this, arguments);

                    if (message?.mesh_file && message.mesh_file[0]) {
                        const filename = message.mesh_file[0];
                        console.log(`[GeomPack VTK Dual] Loading combined mesh: ${filename}`);

                        // Extract mesh A info
                        const meshAVertices = message.mesh_a_vertices?.[0] || 'N/A';
                        const meshAFaces = message.mesh_a_faces?.[0] || 'N/A';
                        const meshAWatertight = message.mesh_a_watertight?.[0];
                        const meshAColor = message.mesh_a_color?.[0] || 'red';

                        // Extract mesh B info
                        const meshBVertices = message.mesh_b_vertices?.[0] || 'N/A';
                        const meshBFaces = message.mesh_b_faces?.[0] || 'N/A';
                        const meshBWatertight = message.mesh_b_watertight?.[0];
                        const meshBColor = message.mesh_b_color?.[0] || 'blue';

                        // Combined mesh info
                        const totalVertices = message.vertex_count?.[0] || 'N/A';
                        const totalFaces = message.face_count?.[0] || 'N/A';

                        // Color mapping for display
                        const colorDisplay = {
                            red: '#ff6b6b',
                            blue: '#64a0ff',
                            green: '#64ff64',
                            yellow: '#ffff64',
                            cyan: '#64ffff',
                            magenta: '#ff64ff',
                            orange: '#ffb464',
                            purple: '#c864ff'
                        };

                        // Build dual mesh info HTML
                        let infoHTML = `
                            <div style="margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #444;">
                                <div style="font-size: 11px; font-weight: bold; color: #fff; margin-bottom: 4px;">Combined Mesh</div>
                                <div style="display: grid; grid-template-columns: auto 1fr; gap: 2px 8px; font-size: 10px;">
                                    <span style="color: #888;">Total Vertices:</span>
                                    <span>${typeof totalVertices === 'number' ? totalVertices.toLocaleString() : totalVertices}</span>
                                    <span style="color: #888;">Total Faces:</span>
                                    <span>${typeof totalFaces === 'number' ? totalFaces.toLocaleString() : totalFaces}</span>
                                </div>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                                <div>
                                    <div style="font-size: 11px; font-weight: bold; margin-bottom: 4px;">
                                        <span style="color: ${colorDisplay[meshAColor] || '#ff6b6b'};">● Mesh A</span>
                                    </div>
                                    <div style="display: grid; grid-template-columns: auto 1fr; gap: 2px 6px; font-size: 9px;">
                                        <span style="color: #888;">Vertices:</span>
                                        <span>${typeof meshAVertices === 'number' ? meshAVertices.toLocaleString() : meshAVertices}</span>
                                        <span style="color: #888;">Faces:</span>
                                        <span>${typeof meshAFaces === 'number' ? meshAFaces.toLocaleString() : meshAFaces}</span>
                        `;

                        if (meshAWatertight !== undefined) {
                            const watertightA = meshAWatertight ? 'Yes' : 'No';
                            const colorA = meshAWatertight ? '#6c6' : '#c66';
                            infoHTML += `
                                        <span style="color: #888;">Watertight:</span>
                                        <span style="color: ${colorA};">${watertightA}</span>
                            `;
                        }

                        infoHTML += `
                                    </div>
                                </div>
                                <div>
                                    <div style="font-size: 11px; font-weight: bold; margin-bottom: 4px;">
                                        <span style="color: ${colorDisplay[meshBColor] || '#64a0ff'};">● Mesh B</span>
                                    </div>
                                    <div style="display: grid; grid-template-columns: auto 1fr; gap: 2px 6px; font-size: 9px;">
                                        <span style="color: #888;">Vertices:</span>
                                        <span>${typeof meshBVertices === 'number' ? meshBVertices.toLocaleString() : meshBVertices}</span>
                                        <span style="color: #888;">Faces:</span>
                                        <span>${typeof meshBFaces === 'number' ? meshBFaces.toLocaleString() : meshBFaces}</span>
                        `;

                        if (meshBWatertight !== undefined) {
                            const watertightB = meshBWatertight ? 'Yes' : 'No';
                            const colorB = meshBWatertight ? '#6c6' : '#c66';
                            infoHTML += `
                                        <span style="color: #888;">Watertight:</span>
                                        <span style="color: ${colorB};">${watertightB}</span>
                            `;
                        }

                        infoHTML += `
                                    </div>
                                </div>
                            </div>
                        `;

                        infoPanel.innerHTML = infoHTML;

                        // Load mesh via ComfyUI view API
                        const filepath = `/view?filename=${encodeURIComponent(filename)}&type=output&subfolder=`;

                        const sendMessage = () => {
                            if (iframe.contentWindow) {
                                console.log(`[GeomPack VTK Dual] Sending postMessage: ${filepath}`);
                                iframe.contentWindow.postMessage({
                                    type: "LOAD_MESH",
                                    filepath: filepath,
                                    timestamp: Date.now()
                                }, "*");
                            } else {
                                console.error("[GeomPack VTK Dual] Iframe contentWindow not available");
                            }
                        };

                        if (iframeLoaded) {
                            sendMessage();
                        } else {
                            setTimeout(sendMessage, 500);
                        }
                    } else {
                        console.log("[GeomPack VTK Dual] No mesh_file in message");
                    }
                };

                return r;
            };
        }
    }
});

console.log("[GeomPack] VTK.js dual mesh preview extension loaded");
