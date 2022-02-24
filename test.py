a = "https://open.spotify.com/artist/5snNHNlYT2UrtZo5HCJkiw?si=ZtU0hn_ZRZyf5YjSM0_LDg"
print(a.index('/artist/'))
print(a[a.index('/artist/') + 8:a.index('?')])