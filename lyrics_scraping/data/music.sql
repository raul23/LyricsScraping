-- Artists
create table artists (
    artist_name text primary key not null -- artist name (e.g. solo, group)

);

-- Songs
create table songs (
    song_title text not null,
    artist_name text not null, -- artist can also be a group
    album_title text not null,
    lyrics_url text not null, -- lyrics' URL (e.g. azlyrics.com)
    lyrics text,
    year text, -- year the song was published
    foreign key(artist_name) references artists(artist_name),
    foreign key(album_title) references albums(album_title),
    primary key(song_title, artist_name, album_title, lyrics_url)
);

-- Albums
create table albums (
    album_title text not null,
    artist_name text not null, -- artist can also be a group
    year text, -- year the album was released
    foreign key(artist_name) references artists(name),
    primary key(album_title, artist_name)
);
