
##
## Use hide() to replace the password-like properties of a JSON document with
## asterix. The routine returns censored copy. The original remains intact.
##

STARS = "*****"

def hide(x):
    if not isinstance(x, dict):
        return x
    doc = x.copy()
    if "Transport" in doc and \
       "Type" in doc["Transport"] and \
       doc["Transport"]["Type"].lower() == "s3":
        if "SecretAccessKey" in doc["Transport"]:
            doc["Transport"]["SecretAccessKey"] = STARS
    return doc

