function actualizarCampos(form) {

    const tipoField = form.querySelector('select[name$="-tipo"]');
    if (!tipoField) return;

    const valor = tipoField.options[tipoField.selectedIndex].text.toLowerCase();

    const campoEnmienda = form.querySelector('select[name$="-subtipo_enmienda"]');
    const filaEnmienda = campoEnmienda ? campoEnmienda.closest('.form-row') || campoEnmienda.closest('.form-group') : null;
    const campoCubierta = form.querySelector('select[name$="-subtipo_cubierta"]');
    const filaCubierta = campoCubierta ? campoCubierta.closest('.form-row') || campoCubierta.closest('.form-group') : null;
    const inputInicial = form.querySelector('input[name$="-nivel_inicial"]');
    const filaInicial = inputInicial ? inputInicial.closest('.field-box') || inputInicial.parentElement : null;
    const inputFinal = form.querySelector('input[name$="-nivel_final"]');
    const filaFinal = inputFinal ? inputFinal.closest('.field-box') || inputFinal.parentElement : null;
    const inputAluminio = form.querySelector('input[name$="-saturacion_aluminio"]');
    const filaAluminio = inputAluminio ? inputAluminio.closest('.field-box') || inputAluminio.parentElement : null;

    // 🔥 OCULTAR TODO SIEMPRE AL INICIO
    if (filaEnmienda) filaEnmienda.style.display = 'none';
    if (filaCubierta) filaCubierta.style.display = 'none';
    if (filaInicial) filaInicial.style.display = 'none';
    if (filaFinal) filaFinal.style.display = 'none';
    if (filaAluminio) filaAluminio.style.display = 'none';
    
    // 🔹 FÓSFORO
    if (valor.includes('fosfor')) {
        if (filaInicial) filaInicial.style.display = '';
        if (filaFinal) filaFinal.style.display = '';
    }

    // 🔹 ENMIENDA
    if (valor.includes('químicos') || valor.includes('enmienda')) {

        if (filaEnmienda) filaEnmienda.style.display = '';

        const subtipoField = form.querySelector('select[name$="-subtipo_enmienda"]');

        if (subtipoField && subtipoField.value) {

            const subtipo = subtipoField.value;

            if (subtipo === 'cal') {
                if (filaAluminio) filaAluminio.style.display = '';
                if (filaFinal) filaFinal.style.display = '';
            }

            else if (subtipo === 'potasio' || subtipo === 'azufre') {
                if (filaInicial) filaInicial.style.display = '';
                if (filaFinal) filaFinal.style.display = '';
            }
        }
    }


    // 👉 SIN SELECCIÓN
    else {
        if (filaInicial) filaInicial.style.display = 'none';
        if (filaAluminio) filaAluminio.style.display = 'none';
    }
    }
    // 🔹 PRADERA
    if (valor.includes('cubierta'))
        if (filaCubierta) filaCubierta.style.display = '';
    

    // 🔥 CONTROL FINAL (FORZADO)
    const subtipoField = form.querySelector('select[name$="-subtipo_enmienda"]');
    const subtipo = subtipoField ? subtipoField.value : null;

    if (subtipo === 'cal') {
        if (filaAluminio) filaAluminio.style.display = '';
    } else {
        if (filaAluminio) filaAluminio.style.display = 'none';
    }

document.addEventListener('DOMContentLoaded', function () {

    function inicializarFormulario(form) {

        const tipoField = form.querySelector('select[name$="-tipo"]');
        if (!tipoField) return;

        form.addEventListener('change', function (e) {
            if (e.target && e.target.name && e.target.name.includes('subtipo_enmienda')) {
                setTimeout(function() {
                    actualizarCampos(form);
                }, 0);
            }
        });

        setTimeout(function() {
            actualizarCampos(form);
        }, 100);
    }

    // 🔥 FORMULARIOS EXISTENTES (FIX REAL)
    document.querySelectorAll('.dynamic-practicapotrero_set').forEach(function(form) {
        inicializarFormulario(form);
    });

    // 🔥 FORMULARIOS NUEVOS (Django inline)
    document.body.addEventListener('formset:added', function(event) {
        const form = event.target;
        inicializarFormulario(form);
    });

});