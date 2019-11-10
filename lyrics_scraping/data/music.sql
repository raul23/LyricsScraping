-- Artists
create table artists (
    artist_name text primary key not null -- artist name (e.g. solo, group)
);

create table artists_urls (
    artist_url text primary key not null, -- artist's URL (e.g. from azlyrics.com)
    artist_name text not null,
    error_on_last_time boolean,
    nb_requests integer not null,
    foreign key(artist_name) references artists(artist_name)
);

-- Songs
create table songs (
    song_title text not null,
    artist_name text not null, -- artist can also be a group
    album_title text not null,
    lyrics text,
    year text, -- year the song was published
    foreign key(artist_name) references artists(artist_name),
    foreign key(album_title) references albums(album_title),
    primary key(song_title, artist_name, album_title)
);

create table songs_urls (
    song_url text primary key not null, -- song's URL (e.g. from azlyrics.com)
    song_title text not null,
    foreign key(song_title) references songs(song_title)
);

-- Albums
create table albums (
    album_title text not null,
    artist_name text not null, -- artist can also be a group
    year text, -- year the album was released
    foreign key(artist_name) references artists(name),
    primary key(album_title, artist_name)
);

create table albums_urls (
    album_url text primary key not null, -- album's URL (e.g. from azlyrics.com)
    album_title text not null,
    foreign key(album_title) references albums(album_title)
);


