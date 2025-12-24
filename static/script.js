document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('bindingForm');
    const generateBtn = document.getElementById('generateBtn');
    const svgContainer = document.getElementById('svgContainer');
    const downloadBtn = document.getElementById('downloadBtn');
    const measurementsPanel = document.getElementById('measurements');
    const measCut = document.getElementById('meas-cut');
    const measHubs = document.getElementById('meas-hubs');

    const measLeatherArea = document.getElementById('meas-leather-area');
    const measLeatherSqft = document.getElementById('meas-leather-sqft');
    const measBoardArea = document.getElementById('meas-board-area');

    const addTextBtn = document.getElementById('addTextBtn');
    const addStampBtn = document.getElementById('addStampBtn');
    const designList = document.getElementById('designList');

    let designElements = [];

    // Helper to redraw design elements UI
    function renderDesignList() {
        designList.innerHTML = '';
        designElements.forEach((elem, index) => {
            const item = document.createElement('div');
            item.className = 'design-item';

            let inputsHtml = '';
            if (elem.type === 'text') {
                inputsHtml = `
                    <div class="design-inputs">
                        <label class="full-width">
                            Content
                            <input type="text" value="${elem.content}" onchange="updateDesignElement(${index}, 'content', this.value)">
                        </label>
                        <label>
                            X (mm)
                            <input type="number" value="${elem.x}" onchange="updateDesignElement(${index}, 'x', this.value)">
                        </label>
                        <label>
                            Y (mm)
                            <input type="number" value="${elem.y}" onchange="updateDesignElement(${index}, 'y', this.value)">
                        </label>
                        <label>
                            Size
                            <input type="number" value="${elem.font_size}" onchange="updateDesignElement(${index}, 'font_size', this.value)">
                        </label>
                    </div>
                `;
            } else if (elem.type === 'stamp') {
                inputsHtml = `
                    <div class="design-inputs">
                        <label class="full-width">
                            Motif
                            <select onchange="updateDesignElement(${index}, 'motif', this.value)">
                                <option value="acorn" ${elem.motif === 'acorn' ? 'selected' : ''}>Acorn</option>
                                <option value="fleuron" ${elem.motif === 'fleuron' ? 'selected' : ''}>Fleuron</option>
                                <option value="corner" ${elem.motif === 'corner' ? 'selected' : ''}>Corner</option>
                            </select>
                        </label>
                        <label>
                            X (mm)
                            <input type="number" value="${elem.x}" onchange="updateDesignElement(${index}, 'x', this.value)">
                        </label>
                        <label>
                            Y (mm)
                            <input type="number" value="${elem.y}" onchange="updateDesignElement(${index}, 'y', this.value)">
                        </label>
                        <label>
                            Scale
                            <input type="number" value="${elem.scale}" step="0.1" onchange="updateDesignElement(${index}, 'scale', this.value)">
                        </label>
                    </div>
                `;
            }

            item.innerHTML = `
                <div class="design-item-header">
                    <span>${elem.type.toUpperCase()}</span>
                    <button type="button" class="remove-btn" onclick="removeDesignElement(${index})">Remove</button>
                </div>
                ${inputsHtml}
            `;
            designList.appendChild(item);
        });
    }

    // Global handlers for the dynamic HTML
    window.updateDesignElement = (index, key, value) => {
        if (key === 'x' || key === 'y' || key === 'font_size' || key === 'scale') {
            value = parseFloat(value) || 0;
        }
        designElements[index][key] = value;
    };

    window.removeDesignElement = (index) => {
        designElements.splice(index, 1);
        renderDesignList();
    };

    addTextBtn.addEventListener('click', () => {
        designElements.push({
            type: 'text',
            content: 'Label',
            x: 50,
            y: 50,
            font_size: 12
        });
        renderDesignList();
    });

    addStampBtn.addEventListener('click', () => {
        designElements.push({
            type: 'stamp',
            motif: 'acorn',
            x: 50,
            y: 50,
            scale: 1.0
        });
        renderDesignList();
    });

    let currentSvgContent = '';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Disable button while processing
        const originalBtnText = generateBtn.textContent;
        generateBtn.textContent = 'Generating...';
        generateBtn.disabled = true;

        // Collect form data
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Manually add border_inset since it might be outside the form tags in the layout
        const borderInput = document.getElementById('border_inset');
        if (borderInput) {
            data.border_inset = borderInput.value;
        }

        data.design_elements = designElements;

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();

            if (result.status === 'success') {
                // Render SVG
                currentSvgContent = result.svg;
                svgContainer.innerHTML = result.svg;

                // Update Measurements
                measCut.textContent = result.measurements.leather_cut || `${result.measurements.width} x ${result.measurements.height}`;

                // Update Material Info
                if (result.measurements.materials) {
                    measLeatherArea.textContent = result.measurements.materials.leather_area_cm2;
                    measLeatherSqft.textContent = result.measurements.materials.leather_area_sqft;
                    measBoardArea.textContent = result.measurements.materials.boards_area_cm2;
                }

                // Clear and populate hubs
                measHubs.innerHTML = '<h4>Hub Positions:</h4><ul>';
                const hubs = result.measurements.hubs || result.measurements.spine_hubs || [];

                // Handle different potential structures from backend
                if (Array.isArray(hubs)) {
                    hubs.forEach(hub => {
                        let text = '';
                        if (typeof hub === 'object' && hub.index) {
                            text = `Hub ${hub.index}: ${hub.position} mm`;
                        } else {
                            // simple strings fallback
                            text = `Hub: ${hub} mm`;
                        }
                        measHubs.innerHTML += `<li>${text}</li>`;
                    });
                }
                measHubs.innerHTML += '</ul>';

                measurementsPanel.classList.remove('hidden');
                downloadBtn.disabled = false;
            } else {
                alert('Error generating template: ' + result.message);
            }

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while communicating with the server.');
        } finally {
            generateBtn.textContent = originalBtnText;
            generateBtn.disabled = false;
        }
    });

    downloadBtn.addEventListener('click', () => {
        if (!currentSvgContent) return;

        const blob = new Blob([currentSvgContent], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'binding_template.svg';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
});
