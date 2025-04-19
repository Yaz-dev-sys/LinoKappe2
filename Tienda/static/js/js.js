document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imagenes');
    const imagePreviews = document.getElementById('image-previews');
    const fileNameDisplay = document.querySelector('.file-name');

    imageInput.addEventListener('change', function() {
        // Limpiar previsualizaciones anteriores
        imagePreviews.innerHTML = '';
        
        const files = this.files;
        if (files.length > 5) {
            alert('Solo puedes subir un máximo de 5 imágenes');
            this.value = '';
            fileNameDisplay.textContent = 'Ningún archivo seleccionado';
            return;
        }
        
        if (files.length > 0) {
            fileNameDisplay.textContent = `${files.length} archivo(s) seleccionado(s)`;
            
            for (let i = 0; i < Math.min(files.length, 5); i++) {
                const file = files[i];
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const previewDiv = document.createElement('div');
                    previewDiv.className = 'image-preview';
                    previewDiv.innerHTML = `
                        <img src="${e.target.result}" alt="Previsualización">
                        <span class="remove-image" data-index="${i}">×</span>
                    `;
                    imagePreviews.appendChild(previewDiv);
                }
                
                reader.readAsDataURL(file);
            }
        } else {
            fileNameDisplay.textContent = 'Ningún archivo seleccionado';
        }
    });

    // Eliminar imágenes seleccionadas
    imagePreviews.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-image')) {
            const index = e.target.getAttribute('data-index');
            const files = Array.from(imageInput.files);
            files.splice(index, 1);
            
            // Crear nueva DataTransfer con los archivos restantes
            const dataTransfer = new DataTransfer();
            files.forEach(file => dataTransfer.items.add(file));
            imageInput.files = dataTransfer.files;
            
            // Disparar evento change para actualizar las previsualizaciones
            const event = new Event('change');
            imageInput.dispatchEvent(event);
        }
    });
});