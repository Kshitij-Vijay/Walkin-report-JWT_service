from auth import hash_password, verify_password

h = hash_password("test123")
print(h)

print(verify_password("test123", h))