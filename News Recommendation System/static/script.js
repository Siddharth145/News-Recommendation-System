document.addEventListener('DOMContentLoaded', function () {
    // Event listener for search button
    document.getElementById('search-button').addEventListener('click', function () {
        var searchQuery = document.getElementById('search-text').value;
        fetchRecommendations(searchQuery);
    });

    // Event listener for Enter key in search input
    document.getElementById('search-text').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            var searchQuery = document.getElementById('search-text').value;
            fetchRecommendations(searchQuery);
        }
    });

    // Event listeners for genre links
    document.querySelectorAll('.nav-links .nav-item').forEach(function (link) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            var genre = this.dataset.genre;
            fetchRecommendations(genre);
        });
    });

    // Fetch random news on page load
    fetchRecommendations('recent news');

    function fetchRecommendations(query) {
        fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'search=' + encodeURIComponent(query)
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                } else {
                    updateCards(data);
                }
            })
            .catch(error => console.error('Error fetching recommendations:', error));
    }

    function updateCards(recommendations) {
        var cardsContainer = document.getElementById('cards-container');
        cardsContainer.innerHTML = '';

        recommendations.forEach(function (newsItem) {
            var template = document.getElementById('template-news-card');
            var clone = template.content.cloneNode(true);
            clone.querySelector('.news-title').textContent = newsItem.headline;
            clone.querySelector('.news-source').textContent = newsItem.source;
            clone.querySelector('.news-desc').textContent = newsItem.abstract;
            clone.querySelector('.news-img').src = newsItem.urlToImage || 'https://via.placeholder.com/400x150';
            clone.querySelector('.news-link').href = newsItem.url;

            var sentimentScoreElement = clone.querySelector('.news-sentiment-score');
            var sentimentEmojiElement = clone.querySelector('.news-sentiment-emoji');

            var sentimentScore = newsItem.sentiment;
            sentimentScoreElement.textContent = sentimentScore.toFixed(2);

            if (sentimentScore >= 0.3) {
                sentimentScoreElement.style.color = 'green';
                sentimentEmojiElement.textContent = '😊';
            } else if (sentimentScore >= -0.2 && sentimentScore < 0.3) {
                sentimentScoreElement.style.color = 'blue';
                sentimentEmojiElement.textContent = '😐';
            } else {
                sentimentScoreElement.style.color = 'red';
                sentimentEmojiElement.textContent = '😢';
            }

            cardsContainer.appendChild(clone);
        });
    }
});
