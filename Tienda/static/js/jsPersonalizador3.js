document.addEventListener('DOMContentLoaded', function() {
    // Constantes y referencias a elementos del DOM
    const DOM = {
        hatCanvas: document.getElementById('hat-canvas'),
        logoPreview: document.getElementById('logo-preview'),
        logoUpload: document.getElementById('logo-upload'),
        uploadBtn: document.getElementById('upload-btn'),
        applyBtn: document.getElementById('apply-btn'),
        resetBtn: document.getElementById('reset-btn'),
        quantityInput: document.getElementById('quantity'),
        decreaseQuantityBtn: document.getElementById('decrease-quantity'),
        increaseQuantityBtn: document.getElementById('increase-quantity'),
        addToCartBtn: document.getElementById('add-to-cart-btn'),
        pedidoModal: document.getElementById('pedido-modal'),
        pedidoForm: document.getElementById('pedido-form'),
        mainImage: document.getElementById('main-image'),
        thumbnailContainer: document.querySelector('.thumbnail-container')
    };

    // Estado de la aplicación
    const state = {
        gorraViews: {},
        currentView: DOM.mainImage.src,
        isDragging: false,
        logoX: 50,
        logoY: 50,
        logoScale: 1.0,
        startX: 0,
        startY: 0,
        maxLogoScale: 3.0,
        minLogoScale: 0.1
    };

    // Inicialización
    init();

    function init() {
        setupEventListeners();
        initializeCurrentView();
        createSizeControls();
    }

    function setupEventListeners() {
        // Eventos de personalización
        DOM.uploadBtn.addEventListener('click', () => DOM.logoUpload.click());
        DOM.logoUpload.addEventListener('change', handleLogoUpload);
        DOM.resetBtn.addEventListener('click', resetCurrentView);
        DOM.applyBtn.addEventListener('click', showPedidoModal);
        DOM.addToCartBtn.addEventListener('click', showPedidoModal);
        DOM.hatCanvas.addEventListener('click', positionLogoOnClick);
        DOM.logoPreview.addEventListener('mousedown', startDragging);
        document.addEventListener('mousemove', handleDragging);
        document.addEventListener('mouseup', stopDragging);
        DOM.logoPreview.addEventListener('wheel', handleLogoScaling);

        // Eventos de cantidad
        if (DOM.quantityInput) {
            DOM.decreaseQuantityBtn.addEventListener('click', decreaseQuantity);
            DOM.increaseQuantityBtn.addEventListener('click', increaseQuantity);
            DOM.quantityInput.addEventListener('change', validateQuantity);
           // DOM.addToCartBtn.addEventListener('click', addToCart);
        }

        // Eventos del modal
        DOM.pedidoForm.addEventListener('submit', handleFormSubmit);
        document.querySelector('.close-btn').addEventListener('click', hidePedidoModal);
    }

    // ============ FUNCIONES DE PERSONALIZACIÓN ============

    function getViewState(viewUrl) {
        if (!state.gorraViews[viewUrl]) {
            state.gorraViews[viewUrl] = {
                logoUrl: '',
                logoX: 50,
                logoY: 50,
                logoScale: 1.0,
                isVisible: false
            };
        }
        return state.gorraViews[viewUrl];
    }

    function saveCurrentState() {
        if (state.currentView) {
            state.gorraViews[state.currentView] = {
                logoUrl: DOM.logoPreview.src,
                logoX: parseInt(DOM.logoPreview.style.left) || 50,
                logoY: parseInt(DOM.logoPreview.style.top) || 50,
                logoScale: state.logoScale,
                isVisible: DOM.logoPreview.style.display === 'block'
            };
        }
    }

    function loadViewState(viewUrl) {
        const viewState = getViewState(viewUrl);
        
        if (viewState.isVisible && viewState.logoUrl) {
            DOM.logoPreview.src = viewState.logoUrl;
            DOM.logoPreview.style.display = 'block';
            DOM.logoPreview.style.left = viewState.logoX + 'px';
            DOM.logoPreview.style.top = viewState.logoY + 'px';
            state.logoX = viewState.logoX;
            state.logoY = viewState.logoY;
            state.logoScale = viewState.logoScale;
            updateLogoSize();
            DOM.applyBtn.disabled = false;
        } else {
            resetLogoPreview();
        }
    }

    function resetLogoPreview() {
        DOM.logoPreview.style.display = 'none';
        DOM.logoPreview.src = '';
        DOM.applyBtn.disabled = true;
    }

    function initializeCurrentView() {
        state.currentView = DOM.mainImage.src;
        getViewState(state.currentView);
    }

    // ============ MANEJO DE LOGO ============

    function handleLogoUpload(e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(event) {
                DOM.logoPreview.src = event.target.result;
                DOM.logoPreview.style.display = 'block';
                DOM.logoPreview.style.left = '50px';
                DOM.logoPreview.style.top = '50px';
                state.logoX = 50;
                state.logoY = 50;
                state.logoScale = 1.0;
                updateLogoSize();
                DOM.applyBtn.disabled = false;
                saveCurrentState();
            };
            
            reader.readAsDataURL(e.target.files[0]);
        }
    }

    function positionLogoOnClick(e) {
        if (DOM.logoPreview.style.display === 'block') {
            const rect = DOM.hatCanvas.getBoundingClientRect();
            state.logoX = e.clientX - rect.left - ((DOM.logoPreview.offsetWidth * state.logoScale) / 2);
            state.logoY = e.clientY - rect.top - ((DOM.logoPreview.offsetHeight * state.logoScale) / 2);
            
            DOM.logoPreview.style.left = state.logoX + 'px';
            DOM.logoPreview.style.top = state.logoY + 'px';
            saveCurrentState();
        }
    }

    // ============ ARRASTRAR Y ESCALAR LOGO ============

    function startDragging(e) {
        if (DOM.logoPreview.style.display === 'block') {
            state.isDragging = true;
            state.startX = e.clientX - state.logoX;
            state.startY = e.clientY - state.logoY;
            e.preventDefault();
        }
    }

    function handleDragging(e) {
        if (state.isDragging) {
            state.logoX = e.clientX - state.startX;
            state.logoY = e.clientY - state.startY;
            
            // Limitar dentro del canvas considerando la escala
            const maxX = DOM.hatCanvas.offsetWidth - (DOM.logoPreview.offsetWidth * state.logoScale);
            const maxY = DOM.hatCanvas.offsetHeight - (DOM.logoPreview.offsetHeight * state.logoScale);
            
            state.logoX = Math.max(0, Math.min(state.logoX, maxX));
            state.logoY = Math.max(0, Math.min(state.logoY, maxY));
            
            DOM.logoPreview.style.left = state.logoX + 'px';
            DOM.logoPreview.style.top = state.logoY + 'px';
        }
    }

    function stopDragging() {
        if (state.isDragging) {
            state.isDragging = false;
            saveCurrentState();
        }
    }

    function handleLogoScaling(e) {
        if (DOM.logoPreview.style.display === 'block') {
            e.preventDefault();
            if (e.deltaY < 0 && state.logoScale < state.maxLogoScale) {
                state.logoScale += 0.05;
            } else if (e.deltaY > 0 && state.logoScale > state.minLogoScale) {
                state.logoScale -= 0.05;
            }
            updateLogoSize();
            saveCurrentState();
        }
    }

    function updateLogoSize() {
        DOM.logoPreview.style.transform = `scale(${state.logoScale})`;
        DOM.logoPreview.style.transformOrigin = 'top left';
        if (document.getElementById('size-value')) {
            document.getElementById('size-value').textContent = `${Math.round(state.logoScale * 100)}%`;
        }
    }

    // ============ CONTROLES DE TAMAÑO ============

    function createSizeControls() {
        const sizeControls = document.createElement('div');
        sizeControls.className = 'size-controls';
        sizeControls.innerHTML = `
            <button id="size-decrease">-</button>
            <span id="size-value">100%</span>
            <button id="size-increase">+</button>
        `;
        
        document.querySelector('.personalizer-controls').appendChild(sizeControls);
        
        document.getElementById('size-decrease').addEventListener('click', decreaseLogoSize);
        document.getElementById('size-increase').addEventListener('click', increaseLogoSize);
    }

    function decreaseLogoSize() {
        if (state.logoScale > state.minLogoScale) {
            state.logoScale -= 0.1;
            updateLogoSize();
            saveCurrentState();
        }
    }

    function increaseLogoSize() {
        if (state.logoScale < state.maxLogoScale) {
            state.logoScale += 0.1;
            updateLogoSize();
            saveCurrentState();
        }
    }

    // ============ MANEJO DE VISTAS MÚLTIPLES ============

    window.changeImage = function(url, element) {
        saveCurrentState();
        
        DOM.mainImage.src = url;
        DOM.hatCanvas.src = url;
        state.currentView = url;
        
        loadViewState(url);
        
        // Actualizar miniaturas activas
        document.querySelectorAll('.thumbnail').forEach(thumb => thumb.classList.remove('active'));
        element.classList.add('active');
    };

    function resetCurrentView() {
        resetLogoPreview();
        state.logoScale = 1.0;
        updateLogoSize();
        
        if (state.currentView) {
            delete state.gorraViews[state.currentView];
        }
    }

    // ============ CANTIDAD Y CARRITO ============

    function decreaseQuantity() {
        let value = parseInt(DOM.quantityInput.value);
        if (value > 1) {
            DOM.quantityInput.value = value - 1;
        }
    }

    function increaseQuantity() {
        let value = parseInt(DOM.quantityInput.value);
        const maxStock = parseInt(DOM.quantityInput.getAttribute('max')) || 99;
        if (value < maxStock) {
            DOM.quantityInput.value = value + 1;
        }
    }

    function validateQuantity() {
        let value = parseInt(this.value);
        const maxStock = parseInt(this.getAttribute('max')) || 99;
        if (isNaN(value) || value < 1) {
            this.value = 1;
        } else if (value > maxStock) {
            this.value = maxStock;
        }
    }

    function addToCart() {
        const quantity = parseInt(DOM.quantityInput.value);
        saveCurrentState();
        
        const personalizaciones = {};
        for (let view in state.gorraViews) {
            if (state.gorraViews[view].isVisible) {
                personalizaciones[view] = {
                    logoUrl: state.gorraViews[view].logoUrl,
                    logoX: state.gorraViews[view].logoX,
                    logoY: state.gorraViews[view].logoY,
                    logoScale: state.gorraViews[view].logoScale
                };
            }
        }
        
        console.log('Datos para el carrito:', {
            cantidad: quantity,
            personalizaciones: personalizaciones
        });
        
        // Reemplazado alert tradicional por SweetAlert2
        Swal.fire({
            title: 'Añadido al carrito',
            text: `Se agregarán ${quantity} gorra(s) personalizadas al carrito`,
            icon: 'success',
            confirmButtonText: 'Continuar'
        });
    }

    // ============ PEDIDO Y MODAL ============

    function showPedidoModal() {
        saveCurrentState();
        const gorraId = getGorraIdFromUrl();
        if (gorraId) {
            document.getElementById('gorra-id-field').value = gorraId;
        }
        DOM.pedidoModal.style.display = 'block';
        prepareCustomizedImages();
    }

    function hidePedidoModal() {
        DOM.pedidoModal.style.display = 'none';
    }

    async function prepareCustomizedImages() {
        try {
            const views = getAvailableViews();
            
            // Limpiar cualquier input de archivo existente primero
            document.querySelectorAll('input[id^="foto"][type="file"]').forEach(el => el.remove());
            document.querySelectorAll('input[id^="foto"][type="hidden"]').forEach(el => el.remove());
            
            for (let i = 0; i < Math.min(views.length, 5); i++) {
                const viewUrl = views[i];
                const viewState = getViewState(viewUrl);
                
                if (viewState.isVisible && viewState.logoUrl) {
                    const imageDataUrl = await captureCustomization(viewUrl);
                    createFileInput(imageDataUrl, i + 1);
                }
            }
            
            // Reemplazado alert tradicional por SweetAlert2
            Swal.fire({
                title: '¡Listo!',
                text: '¡Imágenes preparadas con éxito!',
                icon: 'success',
                confirmButtonText: 'Continuar'
            });
        } catch (error) {
            console.error('Error al preparar las imágenes:', error);
            // Reemplazado alert tradicional por SweetAlert2
            Swal.fire({
                title: 'Error',
                text: `Error al preparar imágenes: ${error.message}`,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    }

    function getAvailableViews() {
        const views = [DOM.mainImage.src];
        document.querySelectorAll('.thumbnail:not(.active) img').forEach(img => {
            if (img.src && !views.includes(img.src)) {
                views.push(img.src);
            }
        });
        return views;
    }

    // Función para capturar la personalización
    async function captureCustomization(viewUrl) {
        return new Promise((resolve, reject) => {
            const tempCanvas = document.createElement('canvas');
            const ctx = tempCanvas.getContext('2d');
            
            const gorraImg = new Image();
            gorraImg.crossOrigin = "Anonymous";
            gorraImg.src = viewUrl;
            
            gorraImg.onload = function() {
                tempCanvas.width = gorraImg.naturalWidth || gorraImg.width;
                tempCanvas.height = gorraImg.naturalHeight || gorraImg.height;
                ctx.drawImage(gorraImg, 0, 0, tempCanvas.width, tempCanvas.height);
                
                const viewState = getViewState(viewUrl);
                if (viewState.isVisible && viewState.logoUrl) {
                    const logoImg = new Image();
                    logoImg.crossOrigin = "Anonymous";
                    logoImg.src = viewState.logoUrl;
                    
                    logoImg.onload = function() {
                        const scaleX = tempCanvas.width / DOM.hatCanvas.offsetWidth;
                        const scaleY = tempCanvas.height / DOM.hatCanvas.offsetHeight;
                        
                        const logoX = viewState.logoX * scaleX;
                        const logoY = viewState.logoY * scaleY;
                        const logoWidth = logoImg.width * viewState.logoScale * scaleX;
                        const logoHeight = logoImg.height * viewState.logoScale * scaleY;
                        
                        ctx.drawImage(logoImg, logoX, logoY, logoWidth, logoHeight);
                        resolve(tempCanvas.toDataURL('image/png'));
                    };
                    
                    logoImg.onerror = () => reject(new Error('Error al cargar el logo'));
                } else {
                    resolve(tempCanvas.toDataURL('image/png'));
                }
            };
            
            gorraImg.onerror = () => reject(new Error('Error al cargar la imagen de la gorra'));
        });
    }

    function createFileInput(imageDataUrl, index) {
        const blob = dataURLtoBlob(imageDataUrl);
        const fileName = `gorra_personalizada_${index}.png`;
        const fileObj = new File([blob], fileName, {type: 'image/png'});
        
        let dataTransfer = new DataTransfer();
        dataTransfer.items.add(fileObj);
        
        // Eliminar cualquier input existente primero
        const existingInput = document.getElementById(`foto${index}-file`);
        if (existingInput) {
            existingInput.remove();
        }
        
        // Crear el input de tipo file
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.id = `foto${index}-file`;
        fileInput.name = `foto${index}`;
        fileInput.style.display = 'none';
        DOM.pedidoForm.appendChild(fileInput);
        
        // Establecer la propiedad files
        fileInput.files = dataTransfer.files;
        
        // Añadir un input oculto para rastrear que tenemos una imagen
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.id = `foto${index}-input`;
        hiddenInput.name = `foto${index}_data`;
        hiddenInput.value = index; // Solo un marcador de que tenemos una imagen
        DOM.pedidoForm.appendChild(hiddenInput);
    }

    function getGorraIdFromUrl() {
        const pathParts = window.location.pathname.split('/');
        const gorraIndex = pathParts.indexOf('gorra');
        if (gorraIndex !== -1 && pathParts[gorraIndex + 1]) {
            return parseInt(pathParts[gorraIndex + 1]);
        }
        return null;
    }
    

    function dataURLtoBlob(dataURL) {
        const parts = dataURL.split(';base64,');
        const contentType = parts[0].split(':')[1];
        const byteString = atob(parts[1]);
        const arrayBuffer = new ArrayBuffer(byteString.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        
        for (let i = 0; i < byteString.length; i++) {
            uint8Array[i] = byteString.charCodeAt(i);
        }
        
        return new Blob([arrayBuffer], {type: contentType});
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        
        try {
            // Asegurarnos de tener las imágenes más recientes listas
            await prepareCustomizedImages();
            
            const formData = new FormData(DOM.pedidoForm);
            
            // Añadir manualmente todos los inputs de archivo para asegurar que se incluyan
            document.querySelectorAll('input[type="file"][id^="foto"]').forEach(fileInput => {
                if (fileInput.files.length > 0) {
                    formData.append(fileInput.name, fileInput.files[0]);
                }
            });
            
            // Reemplazado alert tradicional por SweetAlert2 con loading state
            Swal.fire({
                title: 'Procesando',
                text: 'Enviando pedido...',
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });
            
            const response = await fetch("/crear-pedido/", {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.message || 'Error del servidor');
            if (!data.success) throw new Error(data.errors || 'Error al procesar pedido');
            
            // Cerrar el loading y mostrar éxito
            Swal.fire({
                title: '¡Éxito!',
                text: '¡Pedido realizado con éxito!',
                icon: 'success',
                confirmButtonText: 'Continuar'
            });
            
            hidePedidoModal();
            resetCurrentView();
            
        } catch (error) {
            console.error('Error:', error);
            // Reemplazado alert tradicional por SweetAlert2
            Swal.fire({
                title: 'Error',
                text: error.message || 'Error al procesar tu pedido',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    }
});