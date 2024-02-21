
class Cart():

    def __init__(self, request):
        self.session = request.session

        # get current session key if exists
        cart = self.session.get('session_key')

        #if new user, no session key
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        # make sure cart is available on all pages
        self.cart = cart


    def add(self, url, CRN, title):
        # Check if the CRN is already in the cart
        if CRN not in self.cart:
            # If CRN is not in the cart, add the item
            self.cart[CRN] = {'URL': str(url), 'CRN': str(CRN), 'TITLE': str(title)}
        elif self.cart[CRN]['URL'] != str(url):
            # If the URL is in the cart with a different CRN, add the item
            self.cart[CRN] = {'URL': str(url), 'CRN': str(CRN), 'TITLE': str(title)}

        self.session.modified = True


    def delete(self, CRN_to_delete):
        # Create a list to store the keys to delete
        keys_to_delete = []

        # IF DELETE STOP TO WORK CHANGE TO int(CRN_to_delete)
        # CRN KEEPS CHANGING FROM STR TO INT ON DIFFERENT RUNS OF THE CODE 
        CRN_to_delete = str(CRN_to_delete)

        # Iterate over the dictionary items
        for CRN, item_info in self.cart.items():
            # if we find a match, append it
            if item_info['CRN'] == CRN_to_delete:
                keys_to_delete.append(CRN)

        # Delete the keys outside the loop
        for CRN in keys_to_delete:
            del self.cart[CRN]
        self.session.modified = True


    def __len__(self):
        return len(self.cart)
    

    def get_classes(self):
        # make a dict
        cart_items = []
        # with crn as the key, add this stuff
        for CRN, item_info in self.cart.items():
            cart_items.append({'URL': item_info['URL'], 'CRN': CRN, 'TITLE': item_info['TITLE']})
        return cart_items