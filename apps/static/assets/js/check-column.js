function submit_replace_value(idIAHeader, dropdownID, IAHeader, initiative) {
    var selectedHeader = document.getElementById(dropdownID);
    var csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    var file_name = document.querySelector('input[name="file_name"]').value;
  
    Swal.fire({
      title: "Ganti Kolum",
      text: "Anda pasti anda mahu ganti " + IAHeader + " dengan " + selectedHeader.value + " ?",
      icon: 'warning',
      showCancelButton: true,
      cancelButtonText: 'Batal',
      cancelButtonWidth: 200,
      confirmButtonColor: '#7AC142',
      cancelButtonColor: '#d33',
      confirmButtonText: '  Ya  ',
      allowOutsideClick: false
      }).then((result) => {
        if (result.isConfirmed) {
          $.ajax({
            method:'POST',
            url: $("#replace-url").data('url'),
            headers: {'X-CSRFToken': csrftoken},
            data : {
              selectedHeader : selectedHeader.value,
              IAHeader : IAHeader,
              file_name : file_name,
              csrfmiddlewaretoken : csrftoken,
              initiative : initiative,
              },
              success:function(data)
              {
                data;
                Swal.fire({
                  position: 'middle',
                  icon: 'success',
                  text: 'Nilai telah diubah',
                  timer: 1500,
                  showConfirmButton: false,
                })
                $('#replace-header-'+IAHeader).remove();
                $(".Input option[value="+selectedHeader.value+"]").each(function() {
                  $(this).remove();
              });
              },
              error:function(data){
                alert(data.response);
              }
            })
          }
        })
      }