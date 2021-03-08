from main.utils import MetaApiViewClass, JsonValidation


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.verify_token(return_token_info=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.auth_req.post('/salesman-profile', json=self.request.data)

    @MetaApiViewClass.verify_token(return_token_info=True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.auth_req.put('/salesman-profile', json=self.request.data)
