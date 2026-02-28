import openai 
import config
config.init_config()
embedding_client = openai.OpenAI(
    api_key=config.args.EMBEDDING_APIKEY,
    base_url=config.args.EMBEDDING_URL
)
def my_embeddings_fuction(word):
    # 【修改点 2】：使用专属的 embedding_client 而不是全局的 client
    try:
        completion = embedding_client.embeddings.create(
            model=config.args.EMBEDDING_MODEL,
            input=word
        )
        # 提取并返回向量列表 (维度通常为 1024)
        return completion.data[0].embedding
    except Exception as e:
        print(f"提取向量时出错，错误词汇：{word}，错误信息：{e}")
        # 如果出错，返回一个默认的 1024 维全0向量以防止程序崩溃（针对 bge-m3 的 1024 维）
        return [0.0] * 1024
def add_attribute_to_chromadb(mydb,attribute,emb):#添加词
    id="id{}".format(int(mydb.count())+1)
    mydb.add(
        embeddings=[emb],
        documents=[attribute],
        ids=[id]
    )    
    return 1
def determine_attribute(mydb,emb,num=5):
    results = mydb.query(
    query_embeddings=[emb],
    n_results=num)
    attribute_in_db=results["documents"][0][0:num]
    attribute_id_in_db=results["ids"][0][0:num]
    return attribute_in_db,attribute_id_in_db
def determine_attribute_distance(mydb,emb,num=5):#返回最像的一个词,输入向量
    results = mydb.query(
    query_embeddings=[emb],
    n_results=num)
    attribute_in_db=results["documents"][0][0:num]
    attribute_id_in_db=results["ids"][0][0:num]
    attribute_distance_in_db=results["distances"][0][0:num]
    return attribute_in_db,attribute_id_in_db,attribute_distance_in_db