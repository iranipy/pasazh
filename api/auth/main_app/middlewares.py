# from .schema import JsonValidation
# import fastjsonschema
#
#
# class CheckParamsMiddleWare:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         response = self.get_response(request)
#         schema = JsonValidation.proper_schema(request.path_info.replace('/', ''))
#         validate = fastjsonschema.compile(schema)
#         if validate(request.POST):
#             pass
#
#         return response
