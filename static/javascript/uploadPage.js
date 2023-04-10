
function redirectToPreviousPage() {
    // Récupérer l'adresse de retour
    var previousPage = document.referrer;

    // Vérifier si l'adresse de retour est "127.0.0.1/home"
    if (previousPage.startsWith("http://127.0.0.1:8080/upload")) {
        // Rediriger vers la page "home" en utilisant url_for
        window.location.href = '/home';
    } else {
        // Sinon, retourner à la page précédente normalement
        window.history.back();
    }
}

function checkInputTypeValid() {

    const allowedExtensions = ['jpg', 'jpeg', 'png'];

    document.getElementById('file').addEventListener('change', function (event) {
      const files = event.target.files;

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileExtension = file.name.split('.').pop().toLowerCase();

        if (!allowedExtensions.includes(fileExtension)) {
          alert('Seuls les fichiers jpg, jpeg et png sont autorisés');
          event.target.value = ''; // Supprimez les fichiers sélectionnés
          break;
        }
      }
    });
}