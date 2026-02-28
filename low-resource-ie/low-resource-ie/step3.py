import os
from py2neo import * 
import chromadb
from utils.KG_function import *
from utils.LLM_function import *
from utils.Vector_Database_function import *
import config
config.init_config()

def step1_load_entitys_embedding(load_entitys_embedding,study_area_path,final_path,date):
    embedding_load_history={}
    full_word_table_entitys={}
    if load_entitys_embedding:
        print("正在加载实体嵌入表")
        with open(os.path.join(final_path,"{}实体嵌入表加载历史.txt".format(date)),'r',encoding='utf-8') as file:
            texts=file.readline()
            embedding_load_history=eval(texts)
        full_word_table_entitys=eval(str(embedding_load_history['full_word_table_entitys']))
        print(len(full_word_table_entitys))
        for en in full_word_table_entitys.keys():
            em=full_word_table_entitys[en]['嵌入向量']
            add_attribute_to_chromadb(collection_entitys,en,em)
        
    study_areas=os.listdir(study_area_path)
    for t_study_area in study_areas:
        if load_merge_history is True:
            print("载入对齐历史，跳过实例载入")
            break
        study_area=t_study_area
        if embedding_load_history.get(study_area,-100)!=-100:
            print("已恢复并略过{}".format(study_area))
            continue
        folder_path=os.path.join(study_area_path,t_study_area)
        study_area_files=os.listdir(folder_path)
        for sa_file in study_area_files:
            if sa_file.find(str(date))==-1:
                continue
            with open(os.path.join(folder_path,sa_file),'r',encoding='utf-8') as file:
                texts=file.readline()
                study_area_dict=eval(texts)
            
            temp_word_table_entity=study_area_dict["实例词表"]
            temp_triplet=study_area_dict["全部三元组"]
            
            for word in temp_word_table_entity.keys():
                if full_word_table_entitys.get(word,-100)==-100 :
                    full_word_table_entitys[word]=temp_word_table_entity[word]
                    emb=temp_word_table_entity[word]['嵌入向量']
                    t_label=temp_word_table_entity[word]['类型']
                    add_attribute_to_chromadb(collection_entitys,word,emb)
                
            for tlabel in study_area_dict.keys():
                if tlabel=='全部三元组' or tlabel=='实例词表' or tlabel=='扩展词表'or tlabel=="词类型嵌入表"or tlabel=="属性表"or tlabel=="论文数量":
                    continue
                for entitys in study_area_dict[tlabel].keys():
                    if full_word_table_entitys.get(entitys,-100)==-100:
                        full_word_table_entitys[entitys]={}
                        full_word_table_entitys[entitys]['标签']=tlabel

                        full_word_table_entitys[entitys]['唯一性']="不明"
                        full_word_table_entitys[entitys]['类型']="不明"
                        emb=my_embeddings_fuction(entitys)
                        full_word_table_entitys[entitys]['嵌入向量']=emb
                        add_attribute_to_chromadb(collection_entitys,entitys,emb)

            
        embedding_load_history[study_area]=1
        embedding_load_history['full_word_table_entitys']=full_word_table_entitys
        with open(os.path.join(final_path,"{}实体嵌入表加载历史.txt".format(date)), "w",encoding='utf-8') as f:
            f.write(str(embedding_load_history))
    return full_word_table_entitys

def step2_merge_all(load_merge_history,recover,full_word_table_entitys,final_path,date):
    if load_merge_history is False:
        merage_protect_entity={}
        merge_history_entitys={}
        save_the_graph={}
        word_table_entity_mirror=eval(str(full_word_table_entitys))
        full=len(word_table_entity_mirror)
        if recover is True:
            with open(os.path.join(final_path,"{}对齐中间备份.txt".format(date)),'r',encoding='utf-8') as file:
                texts=file.readline()
                save_the_graph=eval(texts)
            merge_history_entitys=save_the_graph['实例对齐记录']
            full_word_table_entitys=save_the_graph['对齐后实例词表']
            flag=0
            for word in word_table_entity_mirror.keys():#恢复对齐历史
                flag=flag+1
                res=round((flag/full),3)
                print("恢复对齐进度{}%".format(res*100))
                if merge_history_entitys.get(word,-100)!=-100:
                    emb=word_table_entity_mirror[word]['嵌入向量']
                    similar,similarID,similar_distance=determine_attribute_distance(collection_entitys,emb,2)
                    if similar[0]==word:
                        collection_entitys.delete(ids=[similarID[0]])
                    continue
        flag=0
        for word in word_table_entity_mirror.keys():#以后加个已完成百分比
            flag=flag+1
            res=round((flag/full),3)
            print("对齐进度{}%".format(res*100))
            if merge_history_entitys.get(word,-100)!=-100:
                continue
            merge_history_entitys[word]=eval(str(full_word_table_entitys[word]))
            merge_history_entitys[word]['名称']=word
            emb=word_table_entity_mirror[word]['嵌入向量']
            similar,similarID,similar_distance=determine_attribute_distance(collection_entitys,emb,10)
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
                        continue
                    else:
                        tt_result.append(code)
                try:
                    merge_history_entitys[word]=eval(str(full_word_table_entitys[tt_result[0]]))
                    merge_history_entitys[word]['名称']=tt_result[0]
                    merage_protect_entity[word]=1
                    collection_entitys.delete(ids=[mapping[word]['ID']])
                except:
                    print("array为空")
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
                    merge_history_entitys[head]=eval(str(full_word_table_entitys[head]))
                    merge_history_entitys[head]['名称']=head
                    head_array.append(head)
                    merage_protect_entity[head]=1
                    collection_entitys.delete(ids=[mapping[head]['ID']])
                    for u in range(1,len(sp)):
                        if mapping.get(sp[u],-100)==-100 :
                            print("合并时出现未见词，跳过")
                            continue
                        try:
                            if sp[u]!=head and merage_protect_entity.get(sp[u],-100)==-100:
                                del full_word_table_entitys[sp[u]]
                        except:
                            print("{}已经被删除过".format(sp[u]))
                            continue
                        print("删除{},合并到{}".format(sp[u],head))
                        try:
                            merge_history_entitys[sp[u]]=eval(str(full_word_table_entitys[head]))
                        except:
                            merge_history_entitys[sp[u]]=eval(str(merge_history_entitys[head]))
                        merge_history_entitys[sp[u]]['名称']=head
                        collection_entitys.delete(ids=[mapping[sp[u]]['ID']])
            if flag%10==0 and flag!=0:#每10个保存一次
                print("中间过程备份")
                save_the_graph['对齐后实例词表']=full_word_table_entitys
                save_the_graph['实例对齐记录']=merge_history_entitys
                with open(os.path.join(final_path,"{}对齐中间备份.txt".format(date)), "w",encoding='utf-8') as f:
                    f.write(str(save_the_graph))
        save_the_graph['对齐后实例词表']=full_word_table_entitys
        save_the_graph['实例对齐记录']=merge_history_entitys
        with open(os.path.join(final_path,"{}对齐记录.txt".format(date)), "w",encoding='utf-8') as f:
            f.write(str(save_the_graph))
    if load_merge_history is True:
        with open(os.path.join(final_path,"{}对齐记录.txt".format(date)),'r',encoding='utf-8') as file:
            texts=file.readline()
            save_the_graph=eval(texts)
        merge_history_entitys=save_the_graph['实例对齐记录']
        full_word_table_entitys=save_the_graph['对齐后实例词表']
    return merge_history_entitys,full_word_table_entitys

def step3_load2neo4j(study_area_name,study_area_dict,graph_label_entitys,graph_label_attribute,final_entitys,final_tri):
    paper_number=int(study_area_dict['论文数量'])
    study_area_node=create_node_plus(graph_label_entitys,study_area_name,data={'论文数量':paper_number})
    # 【修改点】：将标签设置为“研究区”
    study_area_node.add_label('研究区')
    graph.push(study_area_node)
    attribute_dict=study_area_dict['数值表']
    for attr_label in attribute_dict.keys():
        for item in attribute_dict[attr_label]:
            t=item['内容'].split('#')
            try:
                entity_data=t[1]
                message=t[0]
                origin=item['来源']
            except:
                print("问题属性"+str(item['内容']))
                continue
            if attr_label=='地球化学异常元素符号':
                att_node=create_node_plus(graph_label_attribute,entity_data)
                att_node.add_label(attr_label)
                graph.push(att_node)
                final_tri=if_relation_exist_plus(study_area_node,att_node,attr_label,final_tri,data=study_area_name)
            else:
                att_node=create_node_plus(graph_label_attribute,entity_data,data={'来源':origin,'描述':message})
                att_node.add_label(attr_label)
                graph.push(att_node)
                final_tri=if_relation_exist_plus(study_area_node,att_node,attr_label,final_tri,data=study_area_name)    
    
    t_dict={'type':graph_label_entitys,
            'name':study_area_name,
            'additional_type':'研究区', # 【修改点】
            'data':'空'}
    final_entitys[study_area_name]=t_dict
    
    for label in study_area_dict.keys():
        number_for_label=0
        if label=='全部三元组' or label=='实例词表' or label=='扩展词表'or label=="词类型嵌入表"or label=="数值表"or label=="论文数量":
            continue
        for entitys in study_area_dict[label].keys():
            data={}
            # 兼容空语句占位
            study_area_dict[label][entitys] is None
            
            print(entitys+':')
            if merge_history_entitys.get(entitys,-100)!=-100:
                entity_detial=merge_history_entitys[entitys]
                entitys=entity_detial['名称']
            else:
                try:
                    entity_detial=full_word_table_entitys[entitys]
                except:
                    print(study_area_name)
                    print(entitys)
                    continue
            _only=entity_detial['唯一性']
            
            a_node=create_node_plus(graph_label_entitys,entitys)
            t_dict={'type':[graph_label_entitys],
                    'name':entitys,
                    'additional_type':'空',
                    'data':'空'}
            final_entitys[entitys]=t_dict
            
            final_tri=if_relation_exist_plus(study_area_node,a_node,label,final_tri,data=study_area_name)
            a_node.add_label(label)
            graph.push(a_node)
            number_for_label=number_for_label+1
        # 更新节点属性
        study_area_node=create_node_plus(graph_label_entitys,study_area_name,data={'{}标签下节点数量'.format(str(label)):number_for_label})
    
    #加载完所有属性实体
    tri_array=study_area_dict['全部三元组']
    for tri in tri_array:
        head=tri['head']
        #判断对齐
        if merge_history_entitys.get(head,-100)!=-100:
            head_detail=merge_history_entitys[head]
            head=head_detail['名称']
        else:
            print("不在实例也不在addition，问题词 略过{}".format(head))
            continue
        tail=tri['tail']
        if merge_history_entitys.get(tail,-100)!=-100:
            tail_detail=merge_history_entitys[tail]
            tail=tail_detail['名称']
        else:
            print("不在实例也不在addition，问题词略过{}".format(tail))
            continue
        relation=tri['relation']
        textID=tri['textID']
        article=tri['article']
        data=article+'#'+textID
        
        head_node=create_node_plus(graph_label_entitys,head)
        tail_node=create_node_plus(graph_label_entitys,tail)
        final_tri=if_relation_exist_plus(head_node,tail_node,relation,final_tri,data=data)
    return final_entitys,final_tri

if __name__ == '__main__':
    date=config.args.date
    global_distance=0.6
    load_entitys_embedding=True
    load_merge_history=True
    merge_recover=False
    load2neo4j=True
    graph_label_entitys='{}图谱实体'.format(date)
    graph_label_attribute='{}图谱数值'.format(date)
    
    # 【修改点】：所有路径命名遵循 study_area 逻辑
    study_area_path="./data/{}/step2_result/".format(date)
    final_path="./data/{}/step3_result/".format(date)
    os.makedirs(final_path, exist_ok=True)
    
    chroma_client = chromadb.Client()
    collection_entitys = chroma_client.create_collection(name='collection_entitys')
    save_the_graph={}
    final_entitys={}
    final_tri=[]
    
    full_word_table_entitys=step1_load_entitys_embedding(load_entitys_embedding,study_area_path,final_path,date)
    full_word={}
    full_word['对齐前实例词表']=full_word_table_entitys
    with open(os.path.join(final_path,"{}对齐前记录.txt".format(date)), "w",encoding='utf-8') as f:
        f.write(str(full_word))
        
    merge_history_entitys,full_word_table_entitys=step2_merge_all(load_merge_history,merge_recover,full_word_table_entitys,final_path,date)
    
    if load2neo4j is False:
        print("略过导入neo4j")
    else:
        sa_number=0
        study_areas=os.listdir(study_area_path)
        for sa in study_areas:
            sa_number=sa_number+1
            print(sa+"第{}个研究区/工区，总计{}个".format(sa_number,str(len(study_areas))))
            folder_path=os.path.join(study_area_path,sa)
            sa_files=os.listdir(folder_path)
            for sa_file in sa_files:
                with open(os.path.join(folder_path,sa_file),'r',encoding='utf-8') as file:
                    texts=file.readline()
                    study_area_dict=eval(texts)
                final_entitys,final_tri=step3_load2neo4j(sa,study_area_dict,graph_label_entitys,graph_label_attribute,final_entitys,final_tri)        
        
        save_the_graph['对齐后实例词表']=full_word_table_entitys
        save_the_graph['最终实例节点']=final_entitys
        save_the_graph['最终三元组']=final_tri
        with open(os.path.join(final_path,"{}图谱备份.txt".format(date)), "w",encoding='utf-8') as f:
            f.write(str(save_the_graph))