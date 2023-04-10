//addModal(){
//    document.querySelectorAll('.image-container a').forEach(function(link) {
//      link.addEventListener('click', function(event) {
//        event.preventDefault();
//        const imageElement = link.querySelector('img');
//        const modalImageElement = document.getElementById('modal-image');
//        const imageNameElement = document.getElementById('image-name'); // Récupérer l'élément du nom de l'image
//        modalImageElement.src = imageElement.src;
//        modalImageElement.alt = imageElement.alt;
//        imageNameElement.textContent = imageElement.alt; // Mettre à jour le texte de l'élément avec le nom du fichier
//      });
//    });
//}