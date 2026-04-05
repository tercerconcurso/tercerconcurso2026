function actualizarCampos(form) {

    const tipoField = form.querySelector('select[name$="-tipo"]');
    if (!tipoField) return;

    const valor = tipoField.value;

    const filaEnmienda = form.querySelector('[class*="field-subtipo_enmienda"]');
    const filaCubierta = form.querySelector('[class*="field-subtipo_cubierta"]');
    const inputInicial = form.querySelector('input[name$="-nivel_inicial"]');
    const filaInicial = inputInicial ? inputInicial.closest('.field-box') || inputInicial.parentElement : null;
    const inputFinal = form.querySelector('input[name$="-nivel_final"]');
    const filaFinal = inputFinal ? inputFinal.closest('.field-box') || inputFinal.parentElement : null;
    const inputAluminio = form.querySelector('input[name$="-saturacion_aluminio"]');
    const ficonst filaAluminio = inputAluminio ? inputAluminio.closest('.field-box') || inputAluminio.parentElement : null;

    // 🔥 OCULTAR TODO
    if (filaEnmienda) filaEnmienda.style.display = 'none';
    if (filaCubierta) filaCubierta.style.display = 'none';
    if (filaInicial) filaInicial.style.display = 'none';
    if (filaFinal) filaFinal.style.display = 'none';
    if (filaAluminio) filaAluminio.style.display = 'none';
    
    // 🔹 FÓSFORO
    if (valor === 'fosforo') {
        if (filaInicial) filaInicial.style.display = '';
        if (filaFinal) filaFinal.style.display = '';
    }

    // 🔹 ENMIENDA
if (valor === 'enmienda') {

    if (filaEnmienda) filaEnmienda.style.display = '';
    if (filaFinal) filaFinal.style.display = '';

    const subtipoField = form.querySelector('select[name$="-subtipo_enmienda"]');
    const subtipo = subtipoField ? subtipoField.value : null;

    // 👉 CAL
    if (subtipo === 'cal') {
        if (filaInicial) filaInicial.style.display = 'none';
        if (filaAluminio) filaAluminio.style.display = '';
    }

    // 👉 POTASIO / AZUFRE
    else if (subtipo === 'potasio' || subtipo === 'azufre') {
        if (filaInicial) filaInicial.style.display = '';
        if (filaAluminio) filaAluminio.style.display = 'none';
    }

    // 👉 SIN SELECCIÓN
    else {
        if (filaInicial) filaInicial.style.display = 'none';
        if (filaAluminio) filaAluminio.style.display = 'none';
    }
    }
    // 🔹 PRADERA
    if (valor === 'cubierta') {
        if (filaCubierta) filaCubierta.style.display = '';
    }
    }

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

        const subtipoField = form.querySelector('select[name$="-subtipo_enmienda"]');

        tipoField.addEventListener('change', function () {
            actualizarCampos(form);
        });

        if (subtipoField) {
            subtipoField.addEventListener('change', function () {
                actualizarCampos(form);
            });
        }

        actualizarCampos(form);
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