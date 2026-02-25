document.addEventListener('click', function(e){
    const btn = e.target.closest('.like-btn');
    if(!btn) return;

    const postId = btn.dataset.postId;

    fetch(`/like/${postId}`, {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById(`like-count-${postId}`)
            .innerText = data.count;
    });
});