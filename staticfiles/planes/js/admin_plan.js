document.addEventListener('DOMContentLoaded', function () {

    function toggleMotivo() {
        const estado = document.querySelector('#id_estado_administrativo');
        const motivo = document.querySelector('.field-motivo_rechazo_admin');

        if (!estado || !motivo) return;

        if (estado.value === 'rechazado') {
            motivo.style.display = '';
        } else {
            motivo.style.display = 'none';
        }
    }

    const estado = document.querySelector('#id_estado_administrativo');

    if (estado) {
        estado.addEventListener('change', toggleMotivo);
        toggleMotivo();
    }
});