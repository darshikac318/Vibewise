// Music playlist and recommendation system
class Playlist {
    static currentPlaylist = [];
    static musicDatabase = {
        happy: [
            { title: "Happy", artist: "Pharrell Williams", genre: "Pop" },
            { title: "Can't Stop the Feeling", artist: "Justin Timberlake", genre: "Pop" },
            { title: "Walking on Sunshine", artist: "Katrina and the Waves", genre: "Rock" },
            { title: "Good Vibrations", artist: "The Beach Boys", genre: "Rock" },
            { title: "I Want It That Way", artist: "Backstreet Boys", genre: "Pop" }
        ],
        sad: [
            { title: "Someone Like You", artist: "Adele", genre: "Pop" },
            { title: "Hurt", artist: "Johnny Cash", genre: "Country" },
            { title: "Mad World", artist: "Gary Jules", genre: "Alternative" },
            { title: "Black", artist: "Pearl Jam", genre: "Rock" },
            { title: "Tears in Heaven", artist: "Eric Clapton", genre: "Blues" }
        ],
        angry: [
            { title: "Break Stuff", artist: "Limp Bizkit", genre: "Nu Metal" },
            { title: "Killing in the Name", artist: "Rage Against the Machine", genre: "Rock" },
            { title: "Bodies", artist: "Drowning Pool", genre: "Metal" },
            { title: "Chop Suey!", artist: "System of a Down", genre: "Metal" },
            { title: "Du Hast", artist: "Rammstein", genre: "Industrial" }
        ],
        surprised: [
            { title: "Bohemian Rhapsody", artist: "Queen", genre: "Rock" },
            { title: "Thunderstruck", artist: "AC/DC", genre: "Rock" },
            { title: "Crazy Train", artist: "Ozzy Osbourne", genre: "Metal" },
            { title: "Mr. Blue Sky", artist: "Electric Light Orchestra", genre: "Rock" },
            { title: "Sweet Child O' Mine", artist: "Guns N' Roses", genre: "Rock" }
        ],
        neutral: [
            { title: "Hotel California", artist: "Eagles", genre: "Rock" },
            { title: "Imagine", artist: "John Lennon", genre: "Rock" },
            { title: "The Sound of Silence", artist: "Simon & Garfunkel", genre: "Folk" },
            { title: "Stairway to Heaven", artist: "Led Zeppelin", genre: "Rock" },
            { title: "Comfortably Numb", artist: "Pink Floyd", genre: "Progressive Rock" }
        ]
    };

    static generateRecommendations(mood) {
        const songs = this.musicDatabase[mood] || this.musicDatabase.neutral;
        this.currentPlaylist = [...songs];
        this.shufflePlaylist();
        this.displayPlaylist();
    }

    static shufflePlaylist() {
        for (let i = this.currentPlaylist.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.currentPlaylist[i], this.currentPlaylist[j]] = [this.currentPlaylist[j], this.currentPlaylist[i]];
        }
    }

    static displayPlaylist() {
        const playlistContainer = document.getElementById('playlistContainer');
        if (!playlistContainer) return;

        playlistContainer.innerHTML = '';
        
        this.currentPlaylist.forEach((song, index) => {
            const songElement = this.createSongElement(song, index);
            playlistContainer.appendChild(songElement);
        });
    }

    static createSongElement(song, index) {
        const songDiv = document.createElement('div');
        songDiv.className = 'song-item';
        songDiv.innerHTML = `
            <div class="song-info">
                <h4>${song.title}</h4>
                <p>${song.artist} • ${song.genre}</p>
            </div>
            <button class="play-btn" onclick="Playlist.playSong(${index})">▶</button>
        `;
        return songDiv;
    }

    static playSong(index) {
        const song = this.currentPlaylist[index];
        if (!song) return;

        // Highlight current song
        document.querySelectorAll('.song-item').forEach((item, i) => {
            item.classList.toggle('active', i === index);
        });

        // Update now playing display
        const nowPlaying = document.getElementById('nowPlaying');
        if (nowPlaying) {
            nowPlaying.innerHTML = `
                <strong>Now Playing:</strong> ${song.title} by ${song.artist}
            `;
        }

        console.log(`Playing: ${song.title} by ${song.artist}`);
    }

    static getRecommendationReason(mood) {
        const reasons = {
            happy: "Upbeat songs to keep your energy high!",
            sad: "Gentle melodies to help you process your emotions",
            angry: "High-energy tracks to channel your intensity",
            surprised: "Dynamic songs with unexpected elements",
            neutral: "Balanced classics for a relaxed mood"
        };
        return reasons[mood] || "Great music for any moment";
    }
}

window.Playlist = Playlist;