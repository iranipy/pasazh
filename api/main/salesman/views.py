from main.utils import MetaApiViewClass, JsonValidation


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.post_req('/salesman-profile/', json=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True, return_token_info=True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.token_info['user_id']
        self.put_req('/salesman-profile/', json=dict(**self.request.data))
