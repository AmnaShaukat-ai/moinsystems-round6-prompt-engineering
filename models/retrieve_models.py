from pydantic import BaseModel

class RetrieveRequest(BaseModel):
    query : str 
    top_k : int= 3 

class RetrieveResponse(BaseModel):
    document : list[str]