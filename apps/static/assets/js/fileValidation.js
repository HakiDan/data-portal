document.getElementById('id_Fail').addEventListener('change', parseAndSend);

function fileValidation() {
    var fileInput = document.getElementById('id_Fail');
    var filePath = fileInput.value;
    var allowedExtensions = /(\.xlsx|\.xls)$/i;
    var helaian = document.getElementById("helaian");
    var label_helaian = document.getElementById("label-helaian");

    if (allowedExtensions.exec(filePath)) {
        helaian.style.display = "block";
        label_helaian.style.display = "block";
    } else {
        helaian.style.display = "none";
        label_helaian.style.display = "none";
    }
}

function parseAndSend (event) {
    loadBinaryFile(event,function(data){
        var workbook = XLSX.read(data,{type:'binary'});
        $.each(workbook.SheetNames, function (index, value) {
            $('#helaian').append($('<option/>', { 
                value: value,
                text : value 
            }));
        });
    });
    fileValidation();
}

function loadBinaryFile(path, success) {
    var files = path.target.files;
    var reader = new FileReader();
    var name = files[0].name;
    reader.onload = function(e) {
        var data = e.target.result;
        success(data);
    };
    reader.readAsBinaryString(files[0]);
}