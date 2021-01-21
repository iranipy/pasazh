from main.utils import MetaApiViewClass, JsonValidation


class SalesManView(MetaApiViewClass):

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def post(self, request):
        self.request.data['user_id'] = self.user['id']
        self.post_req('/salesman-profile/', json=dict(**self.request.data))

    @MetaApiViewClass.generic_decor(protected=True)
    @JsonValidation.validate
    def put(self, request):
        self.request.data['user_id'] = self.user['id']
        self.put_req('/salesman-profile/', json=dict(**self.request.data))
