function remark(pk, note){
    Swal.fire({
        title: 'Catatan',
        showConfirmButton: true,
        showCancelButton: false,
        confirmButtonColor: '#7AC142',
        confirmButtonText:'OK',
        allowOutsideClick: false,
        text: note,
    })
}

function reject_note(pk, note){
    Swal.fire({
        title: 'Alasan Ditolak',
        showConfirmButton: true,
        showCancelButton: false,
        confirmButtonColor: '#7AC142',
        confirmButtonText:'OK',
        allowOutsideClick: false,
        text: note,
    })
}