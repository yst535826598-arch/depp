import os
import chromadb
from utils.LLM_function import *
from utils.Vector_Database_function import *
import config
config.init_config()
def load2chromadb(origin,temp_save_dict,collection_entity,full_word_table_entity):
    entitys_biaoqian={}
    for label in origin.keys():
        print(label)
        if label=="实例词表" or label=="全部三元组" or label=="数值表" or temp_save_dict.get(label,-100)==-100:
            continue
        for item in origin[label]:
            print(item)
            try:
                print(origin[label][item][0])
                t_save=origin[label][item][0]
            except:
                print(origin[label][item])
                t_save=origin[label][item]
            
            if temp_save_dict[label].get(item,-100)==-100:
                temp_save_dict[label][item]={}
                entitys_biaoqian[item]=label
            else:
                entitys_biaoqian[item]=label
    word_table_entity=origin["实例词表"]
    for word in word_table_entity.keys():#full_word_table_entity
        flag=0
        t_label='不明'
        if full_word_table_entity.get(word,-100)==-100:
            try:
                t_label=word_table_entity[word]['类型']
                full_word_table_entity[word]=word_table_entity[word]
            except:
                flag=1
                full_word_table_entity[word]={'类型': '', '唯一性': '否', '标签': ''}
            if entitys_biaoqian.get(word,-100)==-100:
                del full_word_table_entity[word]#这里可能有问题，导致后面那么多不在实例表里的词
                continue
            full_word_table_entity[word]['标签']=entitys_biaoqian[word]
            #full_word_table_entity[word]=word_table_entity[word]
            emb=my_embeddings_fuction(word)
            full_word_table_entity[word]['嵌入向量']=emb
            if t_label=='不明' or flag==1:
                #print("这是那种error情况")
                full_word_table_entity[word]['类型']="不明"
                full_word_table_entity[word]['唯一性']="不明"
                t_label="不明"          
            #emb2=my_embeddings_fuction(t_label)
            add_attribute_to_chromadb(collection_entity,word,emb)
    return full_word_table_entity,temp_save_dict,collection_entity
def step1_load(deposits_path,collection_entity):
    full_word_table_entity={}
    temp_save_dict={}
    figure_dict={}
    full_triplet=[]
    figure_label=config.args.KGfigure_labels
    entitys_labels_dict=config.args.KGentity_labels
    for label in figure_label:
        figure_dict[label]=[]
    for label in entitys_labels_dict.keys():
        temp_save_dict[label]={}
    folder1=os.listdir(deposits_path)
    file_number=0
    for files in folder1:
        print(files)
        file_number=file_number+1
        file_path=os.path.join(deposits_path,files)
        with open(file_path,'r',encoding='utf-8') as file:
            texts=file.readline()
            origin_dict=eval(texts)
        for flabel in origin_dict['数值表'].keys():
            for i in origin_dict['数值表'][flabel]:
                figure_dict[flabel].append(i)
        triplet=origin_dict["全部三元组"]
        for tri in triplet:
            temp_tri=eval(str(tri))
            temp_tri['article']=files
            full_triplet.append(temp_tri)
        full_word_table_entity,temp_save_dict,collection_entity=load2chromadb(origin_dict,temp_save_dict,collection_entity,full_word_table_entity)   

    return full_word_table_entity,full_triplet,temp_save_dict,figure_dict,file_number,collection_entity
def step2_merge(word_table_entity_mirror,full_triplet,collection_entity):
    merge_history={}
    for word in word_table_entity_mirror.keys():
        if merge_history.get(word,-100)!=-100:
            continue
        emb=word_table_entity_mirror[word]['嵌入向量']
        similar,similarID,similar_distance=determine_attribute_distance(collection_entity,emb,10)
        mapping={}
        array_4_aligen=[]
        for code in range(0,len(similar)):
            distance=similar_distance[code]
            if distance<global_distance:
                array_4_aligen.append(similar[code])
                mapping[similar[code]]={'ID':similarID[code],
                                        '嵌入向量':word_table_entity_mirror[similar[code]]['嵌入向量'],
                                        '距离':similar_distance[code]
                                        }
        united=level2_merge_special(array_4_aligen)
        if str(united).find('NO')!=-1 or str(united).find('ERROR')!=-1:
            tt_result=[]
            for code in array_4_aligen:
                if code==word:
                    #print("合并时出现未见词，跳过")
                    continue
                else:
                    tt_result.append(code)
            try:
                merge_history[word]=tt_result[0]
            except:
                print("array为空")
            #这里就正常合并
            continue            
        else:
            print(united)
            head_array=[]
            for one in united:
                sp=one.split('#')
                head=sp[0]
                if mapping.get(head,-100)==-100:
                    print("合并时出现未见词，跳过")
                    continue
                merge_history[head]=head
                head_array.append(head)
                collection_entity.delete(ids=[mapping[head]['ID']])
                for u in range(1,len(sp)):
                    if mapping.get(sp[u],-100)==-100 :
                        print("合并时出现未见词，跳过")
                        continue
                    try:
                        local_label=full_word_table_entity[head]['标签']
                        tail_label=full_word_table_entity[sp[u]]['标签']
                        no_sen=temp_save_dict[local_label][head]
                        no_sen=temp_save_dict[tail_label][sp[u]]
                        #temp_save_dict[local_label][head]=temp_save_dict[local_label][head]+temp_save_dict[tail_label][sp[u]]
                    except:
                        continue
                    #print(len(temp_label[i][head]))
                    #print(len(temp_label[i][sp[u]]))
                    temp_save_dict[local_label][head]=[temp_save_dict[local_label][head]].append(temp_save_dict[tail_label][sp[u]])
                    #这里需要改 dict不可以加dict
                    #print(len(temp_label[i][head]))
                    try:
                        del temp_save_dict[tail_label][sp[u]]#假如full_word_table_entity[sp[u]]的标签和temp_save_dict的不一致，或者多个不同标签的，可能会出现删的不完全情况
                        del full_word_table_entity[sp[u]]
                    except:
                        print("{}已经被删除过".format(sp[u]))
                        continue
                    print("删除{},合并到{}".format(sp[u],head))
                    merge_history[sp[u]]=head
                    collection_entity.delete(ids=[mapping[sp[u]]['ID']])
    #三元组替换同义词
    full_triplet_final=[]
    for triplet in full_triplet:
        head=triplet['head']
        tail=triplet['tail']
        relation=triplet['relation']
        if merge_history.get(head,-100)!=-100:
            head=merge_history[head]
        if merge_history.get(tail,-100)!=-100:
            tail=merge_history[tail]
        full_triplet_final.append({
                    'head':head,
                    'tail':tail,
                    'relation':relation,
                    'textID':triplet['textID'],
                    'article':triplet['article']                       
                    })
    return full_word_table_entity,full_triplet_final
if __name__ == '__main__':
    #先对每个矿床的实体合并一轮 假如出问题重启代码即可，有恢复进度功能
    date=config.args.date#'0922'
    global_distance=0.6
    origin_path="./data/{}/step1_result/".format(date)
    result_path1="./data/{}/step2_result/".format(date)
    mission=os.listdir(origin_path)
    num=0
    for deposit_name in mission:
        num=num+1
        print(deposit_name)
        deposits_files_path=os.path.join(origin_path,deposit_name)
        t=os.path.join(result_path1,"{}".format(deposit_name))
        if os.path.exists(os.path.join(t,"{}{}最终合并结果.txt".format(date,deposit_name))) is True:
                print("略过一个已抽取完成文件")
                continue
        else:
            os.makedirs(t, exist_ok=True)
        chroma_client = chromadb.Client()
        collection_entity = chroma_client.create_collection(name='collection_entity{}'.format(str(num)))
        full_word_table_entity,full_triplet,temp_save_dict,figure_dict,file_number,collection_entity=step1_load(deposits_files_path,collection_entity)

        word_table_entity_mirror=eval(str(full_word_table_entity))
        full_word_table_entity,full_triplet_final=step2_merge(word_table_entity_mirror,full_triplet,collection_entity)       

        mirror_temp_save_dict=eval(str(temp_save_dict))

        mirror_temp_save_dict["实例词表"]=full_word_table_entity
        mirror_temp_save_dict["全部三元组"]=full_triplet_final
        mirror_temp_save_dict["数值表"]=figure_dict
        mirror_temp_save_dict["论文数量"]=file_number
        with open(os.path.join(t,"{}{}最终合并结果.txt".format(date,deposit_name)), "w",encoding='utf-8') as f:
            f.write(str(mirror_temp_save_dict))

                    
            
            


    