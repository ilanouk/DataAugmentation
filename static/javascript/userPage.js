

function augmentation(){

    $('#augmentation-form').submit(function(event) {
        // Empecher la soumission du form
        event.preventDefault();

        // Activer la barre de progression
        $('.progress').css('display', 'block');

        // Récupérer les données du formulaire
        var formData = new FormData(this);
        console.log(formData);
//        socketAugmentation = io.connect('http://' + document.domain + ':' + location.port);
//        socket.emit("augmentation", formData);

        // Envoyer la requête AJAX
        $.ajax({
            url: '/home/augmentation',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            async : true,
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                // Il faut rajouter pour gérer l'erreur
                alert('Erreur lors de l\'augmentation des données');
            }
        });

    });
}


function disableRange(optionId,rangeId) {
    const range = document.getElementById(rangeId);
    if (!document.getElementById(optionId).checked) {
          range.disabled = true;
    } else {
          range.disabled = false;
        }
    }


function listenerIntensity(rangeId, intensityId) {
    const range = document.getElementById(rangeId);
    const intensity = document.getElementById(intensityId);
    range.addEventListener('input', (event) => {
        const value = event.target.value;
        intensity.textContent = `${value}%`;
    });
}


function uncheckAll(){
    var checkboxes = document.querySelectorAll('input[type=checkbox][name="to_augment"]');
    // Attendre 0.001 seconde avant de désactiver le bouton
    setTimeout(() => {
          Array.prototype.slice.call(checkboxes).forEach(x => x.checked = false);
    }, 1);
  }

function isAnyChecked() {
  var checkboxes = document.querySelectorAll('input[type=checkbox][name="to_augment"]');
  var checked = Array.prototype.slice.call(checkboxes).some(x => x.checked);
  document.getElementById('btn-augment').disabled = !checked;
}

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('augmentation-form');
    form.addEventListener('submit', function() {
          var intervalID = setInterval(isAnyChecked, 10); // Appelle la fonction toutes les 1 seconde
          setTimeout(function() {
            clearInterval(intervalID); // Arrête l'appel de la fonction après 5 secondes
          }, 1000);
    });
});



function countFilesInFolder(foldername) {
  var count = 0;
 $.ajax({
    url: '/home/countFiles',
    data: { foldername: foldername },
    type: 'POST',
    async: false,
    success: function(data) {
      count = parseInt(data);
      console.log("Nombre de fichiers dans le dossier " + foldername + " : " + count);
    },
    error: function(xhr, status, error) {
      console.error("Une erreur s'est produite lors de l'appel à la fonction countFiles : " + error);
    }
  });
  //alert("Vous avez sélectionné " + count + " fichiers")
  return count;
}


function countSelectedFiles() {

    var inputs = document.querySelectorAll('input[name=to_augment]:checked');
    var count = 0;
    for (var i = 0; i < inputs.length; i++) {
        var filename = inputs[i].value;
        if (filename.endsWith('.jpg') || filename.endsWith('.jpeg') || filename.endsWith('.png')) {
            count++;
        } else {
            count += countFilesInFolder('./uploads/' + filename);
        }
    }
    console.log("Nombre de fichiers total : " + count);
    return count;
}

function updateProgressBar() {
  var count = countSelectedFiles();
  var processedFiles = 0;
  var progressPercent = 0;
  var progressBar = $(".progress-bar");

  progressBar.attr("aria-valuemin", 0);
  progressBar.attr("aria-valuemax", count);

  // Fonction pour mettre à jour la barre de progression
  function updateProgress(nbFilesTraites) {
    processedFiles++;
    progressPercent = Math.round(processedFiles / count * 100);
    progressBar.css("width", progressPercent + "%");
    progressBar.text(progressPercent + "%");

    // Si tous les fichiers sont traités, afficher un message
    console.log("Nombre de fichiers traités : " + processedFiles, "Nombre total de fichiers : " + count);
    if (processedFiles == count) {
        $.ajax({
            url: '/home/download_data',
            type: 'GET',
            xhrFields: {
                responseType: 'blob'
            },
            beforeSend: function() {
                progressBar.addClass("progress-bar-animated");
                progressBar.removeClass("bg-primary");
                progressBar.addClass("bg-warning");
                progressBar.text("Compression en cours...");
            },
            success: function(blob) {
                console.log("Archive ZIP créée avec succès.");
                progressBar.removeClass("progress-bar-animated");
                progressBar.removeClass("bg-warning");
                progressBar.addClass("bg-success");
                progressBar.text("Terminé !");
                // Créer un lien de téléchargement
                var url = window.URL.createObjectURL(blob);
                var a = document.createElement('a');
                a.href = url;
                a.download = 'data.zip';
                // Ajouter le lien au document et cliquer dessus pour lancer le téléchargement
                document.body.appendChild(a);
                a.click();
                // Retirer le lien du document une fois le téléchargement terminé
                document.body.removeChild(a);
            },
            error: function(errorThrown) {
                console.error("Erreur lors de la création de l'archive ZIP :", errorThrown);
                progressBar.removeClass("progress-bar-animated");
                progressBar.removeClass("bg-success");
                progressBar.addClass("bg-danger");
                progressBar.text("Erreur !");
            }

        });
        console.log("Tous les fichiers ont été traités.");
    }
  }

  // Mettre à jour la barre de progression pour chaque socket reçue
  socket.on("updateProgressBar", function(data) {
    console.log(data.progress + " fichiers traités.");
    updateProgress(data.progress);
  });

}


function redirectHome(){

    $.ajax({
        url: '/home',
        type: 'GET',
        async: true,
        success: function(response) {
            // Mettre à jour le contenu de la page avec la réponse
            $('html').html(response);
        },
        error: function(error) {
            // Il faut rajouter pour gérer l'erreur
            alert('Erreur lors de la récupération de la page d\'accueil');
        }
    });

}

