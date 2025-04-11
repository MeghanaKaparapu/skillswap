from werkzeug.security import generate_password_hash, check_password_hash

def sanitize(text):
    return text.strip().lower()

def create_offer_document(user, skill_offer, skill_want):
    return {
        "user": user.strip(),
        "skill_offer": sanitize(skill_offer),
        "skill_want": sanitize(skill_want),
        "matched": False
    }

def match_offers(offers):
    matched_pairs = []
    used_ids = set()

    for i in range(len(offers)):
        for j in range(i + 1, len(offers)):
            offer1 = offers[i]
            offer2 = offers[j]

            if offer1["_id"] in used_ids or offer2["_id"] in used_ids:
                continue

            if offer1["skill_offer"] == offer2["skill_want"] and offer1["skill_want"] == offer2["skill_offer"]:
                matched_pairs.append({
                    "user1": offer1["user"],
                    "user1_offers": offer1["skill_offer"],
                    "user1_wants": offer1["skill_want"],
                    "user2": offer2["user"],
                    "user2_offers": offer2["skill_offer"],
                    "user2_wants": offer2["skill_want"],
                })
                used_ids.add(offer1["_id"])
                used_ids.add(offer2["_id"])

    return matched_pairs

def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored, provided):
    return check_password_hash(stored, provided)
