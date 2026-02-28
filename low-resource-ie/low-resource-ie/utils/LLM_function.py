from openai import OpenAI
import time
import config
config.init_config()
def ask_llm_base(question,system_prompt='你是一名地质专家，我需要你回答一些专业地质问题。',mykey=config.args.APIKEY,mybase_url=config.args.URL,mymodel=config.args.model):
    time.sleep(0.05)
    client = OpenAI(
        api_key=mykey,  # 替换成真实DashScope的API_KEY
        base_url=mybase_url,  # 填写DashScope服务endpoint
    )
    chat_completion = client.chat.completions.create(
    temperature=0.5,
    model=mymodel,
    messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': question
            }
        ],
    max_tokens=1000,
    )
    return chat_completion.choices[0].message.content
def llm_check_part_array(p1,p2,time=3,mymodel='default'):
    flag=time
    while(flag):
        if mymodel!='default':
            answer=ask_llm_base(question=p2,system_prompt=p1,mymodel=mymodel)
        else:
            answer=ask_llm_base(question=p2,system_prompt=p1)
        print(answer)
        start=answer.find('ARRAYSTART')
        end=answer.find('ARRAYEND')
        if start!=-1 and end!=-1:
            mydict=answer[start+11:end]
            try:
                start=mydict.find('[')
                end=mydict.rfind(']')
                mydict=mydict[start:end+1]
                mydict=mydict.replace('/','')
                mydict=eval(mydict)
                if type(mydict) is not list or type(mydict) is tuple:
                    raise KeyError
                break
            except:
                print("回答不合格，重复中")
                print(answer)
                flag=flag-1
                continue
        else:            
            print("回答不合格，重复中")
            print(answer)
            flag=flag-1
            continue
    if flag==0:
        return "ERROR"
    return mydict 
def llm_check_part_dict(p1,p2,time=3,mymodel='default'):
    flag=time
    while(flag):
        if mymodel!='default':
            answer=ask_llm_base(question=p2,system_prompt=p1,mymodel=mymodel)
        else:
            answer=ask_llm_base(question=p2,system_prompt=p1)
        print(answer)
        start=answer.find('ARRAYSTART')
        end=answer.find('ARRAYEND')
        if start!=-1 and end!=-1:
            mydict=answer[start+11:end]
            try:
                start=mydict.find('{')
                end=mydict.rfind('}')
                mydict=mydict[start:end+1]
                mydict=mydict.replace('/','')
                mydict=eval(mydict)
                if type(mydict) is not dict or type(mydict) is tuple:
                    print(mydict)
                    raise ValueError("发现非字典输出")
                break
            except:
                print("回答不合格，重复中")
                print(answer)
                flag=flag-1
                continue
        else:            
            print("回答不合格，重复中")
            print(answer)
            flag=flag-1
            continue
    if flag==0:
        return "ERROR"
    return mydict 
def llm_check_YESNO(p1,p2,time=3,mymodel='default'):
    flag=time
    while(flag):
        if mymodel!='default':
            answer=ask_llm_base(question=p2,system_prompt=p1,mymodel=mymodel)
        else:
            answer=ask_llm_base(question=p2,system_prompt=p1)
        print(answer)
        start=answer.find('ARRAYSTART')
        end=answer.find('ARRAYEND')
        reason=answer[end+9:]
        if start!=-1 and end!=-1:
            mydict=answer[start+11:end]
            try:
                if mydict.find('YES')!=-1:
                    return True,reason
                if mydict.find('NO')!=-1:
                    return False,reason
                break
            except:
                print("回答不合格，重复中")
                print(answer)
                flag=flag-1
                continue
        else:            
            print("回答不合格，重复中")
            print(answer)
            flag=flag-1
            continue
    if flag==0:
        return False,"空"
    return False,"空"
def level2_check(question,answer):
    p1="你是一名地质专家，我需要你协助我确认收集的信息是否有明显错误。如果有错误，请简短指出并提供改正方法"
    p2="信息收集是通过问答的形式进行的，完整的问题如下："+question+"获得信息如下："+answer+"\n.如果收集到的信息有明显错误，例如回答不符合问题要求、收集的信息与原文不符，请回答NO。如果没有明显错误，请回答YES。你在回答划分结果时必须严格遵守以下的格式，回答前后使用ARRAYSTART和ARRAYEND作为标识。格式样例:ARRAYSTART YES或NO ARRAYEND "
    mydict,reason=llm_check_YESNO(p1,p2,time=3)      
    return mydict,reason
def level1_entity(text):
    p1="你是一名地质专家，你的任务是从一段话中抽取地质实例。由于矿床名称在其他步骤中已提取，你回答的地质实例不应包括具体矿床，例如坪水金矿。你应全程使用中文回答。"
    p2="我会给出一段话，这段话描述一个矿床的部分属性。这些属性里包含其他的抽象地质概念和地质实例，你的任务就是从中提取这些地质实例。你需要注意你只能从信息中抽取除矿床以外的地质实例，而非抽象地质概念。具体来说，板块是一个抽象地质概念，而太平洋板块是这个抽象地质概念下的一个地质实例并且不是一个具体的矿床，所以你应选择太平洋板块，同时忽略俯冲太平洋板块这样的同义词，其他地质实例以此类推。同时诸如你的回答必须严格遵守python字符串数组的格式，回答前后使用ARRAYSTART和ARRAYEND作为标识。回答格式样例:ARRAYSTART ['除金矿床以外的地质概念或实体'] ARRAYEND 你要抽取的一段话是:"+text
    check_part="我会给出一段话，这段话描述一个矿床的部分属性。这些属性里包含其他的抽象地质概念和地质实例，你的任务就是从中提取这些地质实例。你需要注意你只能从信息中抽取除矿床以外的地质实例，而非抽象地质概念。具体来说，板块是一个抽象地质概念，而太平洋板块是这个抽象地质概念下的一个地质实例并且不是一个具体的矿床，所以你应选择太平洋板块，同时忽略俯冲太平洋板块这样的同义词，其他地质实例以此类推。你要抽取的一段话是:"+text
    my_time=4
    reason=""
    while(my_time>0):
        mydict=llm_check_part_array(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=3)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:
           print(mydict)
           return mydict 
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
def level1_entity_forPhenomenon(text):
    p1="你是一名深部地球物理与地质专家，你的任务是从一段话中抽取明确且信息丰富的地质与地球物理现象。具体指岩浆活动、板块俯冲、深部热动力过程、地震波异常、电磁感应现象等，不包括公式和数值。由于研究区/工区名称已提取，你回答的内容不应包括具体的研究区名字。你应全程使用中文回答。"
    
    p2="我会给出一段话，描述深部探测的属性。你的任务是提取地质与地球物理现象。例如：低阻异常、地震波速衰减、莫霍面隆起、地幔柱上涌。你的回答必须严格遵守python字符串数组的格式，前后使用ARRAYSTART和ARRAYEND作为标识。格式样例:ARRAYSTART ['低阻异常','地幔柱上涌'] ARRAYEND 你要抽取的一段话是:"+text
    
    check_part="你的任务是提取地质与地球物理现象。例如：低阻异常、地震波速衰减、莫霍面隆起、地幔柱上涌。你要抽取的一段话是:"+text
    my_time=4
    reason=""
    while(my_time>0):
        mydict=llm_check_part_array(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=3)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:
           print(mydict)
           return mydict 
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
def level1_entity_forConcept(text):
    p1="你是一名地球物理专家，你的任务是从一段话中抽取明确的探测仪器、算法、处理技术、深部构造层（如莫霍面、软流圈）等地质/物探名词。不包括公式和数值。你应全程使用中文回答。"
    
    p2="我会给出一段话。你需要从中提取物探或地质名词。例如：大地电磁测深、逆时偏移、三分量检波器、断裂带、岩石圈地幔。你的回答必须严格遵守python字符串数组的格式。格式样例:ARRAYSTART ['大地电磁测深','逆时偏移'] ARRAYEND 你要抽取的一段话是:"+text
    
    check_part="你的任务是提取物探或地质名词。例如：大地电磁测深、逆时偏移、三分量检波器、断裂带、岩石圈地幔。你要抽取的一段话是:"+text
    my_time=4
    reason=""
    while(my_time>0):
        mydict=llm_check_part_array(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=3)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:
           print(mydict)
           return mydict 
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
def level1_entity_forExample(text):
    p1="你是一名深部地球物理与地质专家，你的任务是从一段话中抽取具体的深地探测或地质实例，不包括公式和数值。由于工区/研究区名称已提取，你的回答不应包括具体研究区名字。你应全程使用中文回答。"
    
    p2="我会给出一段描述深部探测的文字，请提取其中的具体实例。具体来说，“断裂带”是抽象概念，而“郯庐断裂带”是实例；“地震台网”是概念，而“国家地震观测台网”是实例。回答必须严格遵守python字符串数组格式。回答样例:ARRAYSTART ['除研究区以外的具体实例'] ARRAYEND 你要抽取的一段话是:"+text
    
    check_part="任务是从信息中抽取具体实例。例如“郯庐断裂带”、“国家地震观测台网”。你要抽取的一段话是:"+text
    my_time=4
    reason=""
    while(my_time>0):
        mydict=llm_check_part_array(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=3)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:
           print(mydict)
           return mydict 
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
def level1_entity_forfigure(text):
    p1="你是一名深部地球物理与地质专家，你的任务是从一段话中抽取具备科学意义的数字或符号形式的观测与反演参数。你应全程使用中文回答。"
    
    p2="我会给出一段描述深部探测的文字。你需要提取数值或符号信息，例如：地震波速6.5km/s中的6.5km/s、探测深度50km中的50km、数据分辨率10m中的10m、电阻率100Ω·m中的100Ω·m。你需要同时用一个词回答其含义。回答样例:ARRAYSTART ['探测深度#50km','波速#6.5km/s'] ARRAYEND 若无信息回答ARRAYSTART ['无#无'] ARRAYEND 你要抽取的一段话是:"+text
    
    check_part="任务是提取数值或符号信息，例如：地震波速6.5km/s中的6.5km/s、探测深度50km中的50km、数据分辨率10m中的10m。需同时给出含义。你要抽取的一段话是:"+text
    my_time=1
    reason=""
    while(my_time>0):
        mydict=llm_check_part_array(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=3)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:
           print(mydict)
           return mydict 
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
def level1_entity_multiple_strategy(text,strategy='single',repetitions=1):#multiple
    flag=0
    result_dict={}
    result_array=[]
    result_dict_figure={}
    result_array_figure=[]
    if strategy=='single':
        while(flag<repetitions):
            flag=flag+1
            entitys=level1_entity(text)
            for i in entitys:
                if result_dict.get(i,-100)==-100:
                    result_dict[i]=1
    if strategy=='multiple':
        while(flag<repetitions):
            flag=flag+1
            entitys_Phenomenon=level1_entity_forPhenomenon(text)
            entitys_Example=level1_entity_forExample(text)
            entitys_Concept=level1_entity_forConcept(text)
            entitys_figure=level1_entity_forfigure(text)
            for i in entitys_Concept:
                if result_dict.get(i,-100)==-100:
                    result_dict[i]=1
            for i in entitys_Example:
                if result_dict.get(i,-100)==-100:
                    result_dict[i]=1
            for i in entitys_Phenomenon:
                if result_dict.get(i,-100)==-100:
                    result_dict[i]=1
            for i in entitys_figure:
                if result_dict_figure.get(i,-100)==-100 and i!='无#无':
                    result_dict_figure[i]=1
    for entity in result_dict.keys():
        result_array.append(entity)
    for entity in result_dict_figure.keys():
        result_array_figure.append(entity)
    return result_array,result_array_figure
def level1_entity_label_single(entity,text,label):
    print(label)
    p1="你是一名深部地球物理与地质专家，我需要你阅读一段文字，并将指定名词划分到预定义的类别中。"
    
    p2="我有提取到的名词[{}]，你需要依据上下文将其划分到以下类别术语{}中。请注意你只能回答术语中的一个类别。你在回答划分结果时必须严格遵守python字典的格式。回答样例:ARRAYSTART {{'地质名词':'类别'}} ARRAYEND 分类样例 '三分量检波器':'地震探测仪器','逆时偏移':'地震反演','郯庐断裂带':'断裂'。 这个名词抽取自这一段话:".format(str(entity),str(label))+text
    
    check_part="我有提取到的名词[{}]，需要划分到类别术语{}中。只能回答给定类别中的一个。分类样例 '三分量检波器':'地震探测仪器','逆时偏移':'地震反演'。".format(str(entity),str(label))+" 这些名词是{} 抽取自:".format(str(entity))+text
    my_time=3
    reason=""
    while(my_time>0):
        mydict=llm_check_part_dict(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=3)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:
            flag=0
            for key in mydict.keys():
                for biaozhun in label:
                    try:
                        if mydict[key]==biaozhun or mydict[key].find(biaozhun)!=-1 or biaozhun.find(mydict[key])!=-1:
                            ccc=1
                    except:
                        flag=flag-1
                        continue

                    if mydict[key]==biaozhun or mydict[key].find(biaozhun)!=-1 or biaozhun.find(mydict[key])!=-1:
                       mydict[key]=biaozhun
                       flag=flag+1
                       #print(mydict[key])
                       #print(biaozhun)
                       break
            if flag>=len(mydict) and mydict.get(entity,-100)!=-100:
                return mydict[entity]
            else:
                my_time=my_time-1
                continue
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
def level2_relation_extract(entity,text):#地层
    p1="你是一名地球物理专家，你的任务是抽取一段文字中指定词汇间的关系，并以三元组的形式回答。"
    p2="我提取了以下概念:{}。你需要找到它们间的关系。必须符合以下关系定义：应用关系：算法→数据（逆时偏移，作用于，地震数据）。指示关系：异常数据→地质体（低阻异常，指示，隐伏断裂）。产出/生成关系：算法/仪器→成果（层析成像，生成，速度模型）。空间关系：构造→构造（上地壳，位于，下地壳之上）。验证关系：成果A→成果B（电磁解释成果，验证于，地震解释成果）。回答格式样例:ARRAYSTART ['逆时偏移#地震数据#作用于'] ARRAYEND 这段文字是:".format(str(entity))+text
    check_part="我提取了以下概念:{}。必须符合以下关系定义：应用关系：算法→数据（逆时偏移，作用于，地震数据）。指示关系：异常数据→地质体（低阻异常，指示，隐伏断裂）。产出/生成关系：算法/仪器→成果（层析成像，生成，速度模型）。空间关系：构造→构造（上地壳，位于，下地壳之上）。验证关系：成果A→成果B（电磁解释成果，验证于，地震解释成果）。回答格式样例:ARRAYSTART ['逆时偏移#地震数据#作用于'] ARRAYEND 这段文字是:".format(str(entity))+text
    my_time=2
    reason=""
    while(my_time>0):
        mydict=llm_check_part_array(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=5)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:    
            if str(mydict).find('{')!=-1:
                continue
            return mydict 
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
def level2_merge_special(entitys):#地层
    p1="你是一名深部地球物理与地质专家，你的任务是阅读多个词汇，并回答其中的同义词。"
    
    p2="我提取到了以下地质/物探概念:{}。你的任务是找出完全同义的词并挑选一个最优词，随后回答哪些词会被合并到最优词上。只有完全同义的词可以合并，例如'MT'和'大地电磁测深'，'三分量检波器'和'三轴检波器'，'莫霍面'和'Moho面'。绝对不可将子概念合并到父级概念上，例如'面波'与'地震波'不可以，因为面波属于地震波；'上地壳'与'地壳'不可以。如果没有可合并的词，请回答NO。回答格式必须严格遵守python字符串数组的格式，前后使用ARRAYSTART和ARRAYEND作为标识。回答样例:ARRAYSTART ['最优词#被合并词1#被合并词2'] ARRAYEND 无可合并词时样例:ARRAYSTART ['NO'] ARRAYEND ".format(str(entitys))
    
    check_part="我提取到了以下地质/物探概念:{}。找出完全同义的词并回答哪些词会被合并到最优词上。只有完全同义的词可以合并（如'MT'和'大地电磁测深'）。绝对不可将子概念合并到父级概念（如'面波'与'地震波'）。如果没有可合并的词请回答NO。格式需严格遵守标识。".format(str(entitys))
    my_time=2
    reason=""
    while(my_time>0):
        mydict=llm_check_part_array(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=5)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:           
           return mydict 
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
def level2_merge_entity2addition(entitys,special):#地层
    p1="你是一名深部地球物理与地质专家，你的任务是阅读多个词汇，并回答特定一个词的同义词。"
    
    p2="我提取了概念词组D:{}，以及特定词A:{}。你的任务是从D中找出A的完全同义词，并回答哪些词会被合并到A上。例如'MT'和'大地电磁测深'。绝对不可将子概念合并到父级概念，例如'面波'与'地震波'不可以。如果没有可合并词，请回答NO。回答格式严格遵守python字符串数组格式，前后使用ARRAYSTART和ARRAYEND作为标识。回答样例:ARRAYSTART ['特定词A#被合并词1#被合并词2'] ARRAYEND 无可合并词时样例:ARRAYSTART ['NO'] ARRAYEND ".format(str(entitys),special)
    
    check_part="我提取了概念词组D:{}，以及特定词A:{}。任务是从D中找出A的完全同义词并回答合并关系。只有完全同义可合并（如'莫霍面'和'Moho面'）。绝对不可将子概念合并到父概念。如果没有可合并的词，请回答NO。".format(str(entitys),special)
    my_time=2
    reason=""
    while(my_time>0):
        mydict=llm_check_part_array(p1+"请注意你在上一次回答同样问题时出错，出错内容和更正思路如下:"+reason,p2,time=5)
        if mydict=="ERROR":
            my_time=my_time-1
            continue
        r,reason=level2_check(check_part,str(mydict))
        if r:           
           return mydict 
        else:
            my_time=my_time-1
            continue
    print("超过最大次数退出")
    return "ERROR"
