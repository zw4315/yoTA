# Detected language: en (p=1.00)
<!-- json weston 做这个作者的调研 -->
[0.00s -> 6.16s]  Now, I don't know about you, but these days I'm using AI in my everyday life quite a
[6.16s -> 13.32s]  lot to help me create art, write code, write formal letters, ask questions, brainstorm,
[13.32s -> 14.80s]  all kinds of stuff.
[14.80s -> 19.08s]  And that's only really been possible very recently.
[19.08s -> 25.44s]  I think AI researchers are pretty privileged to be in this time in human history and
[25.44s -> 30.60s]  see these improvements happening in real time.
[30.60s -> 36.52s]  And we've seen how quickly they evolve, but I still think there's a lot left to do.
[36.52s -> 44.68s]  I think we can expect still more large improvements even in the near future and next few years.
[44.68s -> 55.00s]  And we've seen that even in the last months, right, with 01, R1, and so on, big improvements
[55.00s -> 58.52s]  in various benchmarks in reasoning.
[58.52s -> 67.52s]  And after all that, it's a very young field overall, but that subfield with learning chain
[67.52s -> 71.24s]  of thought, I mean chain of thought itself is only really from 2022.
[71.24s -> 77.74s]  So yeah, I think it's really impressive how fast things are moving.
[77.74s -> 87.18s]  So in the context of this talk, I'm going to be talking about methods for self-improving
[87.18s -> 88.18s]  language models.
[88.18s -> 91.54s]  And that means getting better at tasks.
[91.54s -> 95.38s]  In particular, that will mean that they're getting better at reasoning so that they
[95.38s -> 98.84s]  can get better at those tasks.
[98.84s -> 107.96s]  So for an AI to train itself, that means it needs to do this introspection as it's training.
[107.96s -> 114.80s]  So normal classical training was like this fixed dataset, and it would learn from it.
[114.80s -> 122.88s]  But that's moving now a little bit where in **reinforcement learning** setups, and particularly
[122.88s -> 128.76s]  with reinforcement learning from AI feedback, models are training themselves in a much more
[128.76s -> 130.32s]  sophisticated way.
[130.32s -> 135.20s]  For example, we can imagine models that create new challenges, tasks to train themselves
[135.20s -> 136.20s]  on.
<!-- 有点像 control 里面的正循环的知识 -->
[136.20s -> 139.56s]  They can evaluate themselves, whether they're getting them right, we call that self-rewarding,
[139.56s -> 142.48s]  and then update themselves based on what they've understood.
[142.48s -> 148.00s]  So that means then they're going to be getting more knowledge, more reasoning ability.
[148.00s -> 155.12s]  And so a research question is, can they do this kind of training on themselves?
[155.12s -> 157.92s]  And can that help them become superhuman?
[157.92s -> 163.92s]  So I have a picture down here of one particular approach for that that's called self-rewarding
[163.92s -> 169.80s]  language models, which I'm going to be talking about a bit later.
[169.80s -> 174.94s]  But in terms of reasoning, when we're doing this kind of self-improving, you can look
[174.94s -> 180.50s]  at this as like **two different ways** of improving reasoning.
<!-- 系统1 vs 系统2 -->
<!-- 系统1：
- 常见问题：忽略细节 + 幻觉
- COT 可以帮改进
- 感觉是快慢系统的快系统，心理学
 -->
[180.50s -> 185.84s]  So these are called system one and system two sometimes by people.
<!-- TODO: 怎么理解这个 reactive and associations -->
[185.84s -> 193.56s]  So system one, like in humans, we see that as reactive and relies on associations.
[193.56s -> 198.40s]  And in machine learning models or LLMs, it can be the same thing.
[198.40s -> 205.64s]  So you can think of the **transformer** itself, like the neural network, as this kind of
[205.64s -> 207.86s]  performing this system one reasoning.
[207.86s -> 212.92s]  So where you have these hidden states in the neural network that's going through a
[212.92s -> 221.58s]  whole bunch of multiplications, attentions, and so on, that can be seen as your system
[221.58s -> 222.72s]  one reasoning.
[222.72s -> 225.52s]  So in that case, you have a fixed compute per token.
[225.52s -> 228.32s]  You're directly outputting the answer.
[228.32s -> 232.84s]  But there's some problems with LLMs as we have them now.
<!-- 大模型的幻觉问题 -->
[232.84s -> 238.62s]  In particular, they can learn spurious unwanted correlations, there's hallucination, sick
[238.62s -> 243.18s]  of fancy, jailbreaking, and I'm going to show some of those things later.
[243.18s -> 246.90s]  And then you can try and fix this stuff with what's called system two.
[246.90s -> 249.66s]  So that's more deliberate and effortful thinking.

<!-- cot 是怎么做到慢系统的 -->
[249.66s -> 257.78s]  And the most common way we think of that system two today is by generating language
[257.78s -> 259.90s]  tokens that are a chain of thought.
<!-- 对系统1 的巧妙总结，很像一个计算机，给它一些数字，它返回一些数字，所谓的传统的大模型就是如此 -->
[259.90s -> 265.70s]  So now that's not just pushing these numbers through the neural net, you're actually looking
[265.70s -> 272.42s]  at the tokens, the neural net outputs as a thought stream before the final tokens that
[272.42s -> 275.30s]  will be the final response.

<!-- 我觉得理论可能暂时也解释不好为什么 COT 有用 -->
[275.30s -> 281.98s]  Now what's powerful when you do that is that that system two chain of thought reasoning
[281.98s -> 290.10s]  can actually do a whole bunch of stuff like：
- planning, 
- search, 
- verification, various
[290.10s -> 297.82s]  kinds of reasoning, even though it's generating sort of autoregressively left to right, it
[297.82s -> 304.38s]  could still potentially do all that kind of sets of thoughts, as you'll see models
[304.38s -> 309.14s]  like DeepSeek 01, 03 can do.
[309.14s -> 314.62s]  So yeah, so those are the two kinds of things that we can effectively improve in, try and
[314.62s -> 318.94s]  improve like the **architecture** or the **weights** of the model and improve system one, or
[318.94s -> 324.26s]  try and improve how it generates these chains of thought or other ways of doing system
[324.26s -> 326.58s]  two before it outputs a response.

[326.58s -> 333.42s]  I mean, obviously they're related because it's the same language model doing both things.
[333.42s -> 339.70s]  So that's the goal, try and do this self-learning to improve these things.
[339.70s -> 347.34s]  First I'm going to go through some history of how we got where we are like today and
[347.34s -> 354.22s]  then talk about more recent works from the last year or so after I go through this history.
<!-- 第一个阶段是 pre-history 史前时期 -->
[354.22s -> 359.02s]  But before we're going to start pre-2020, so pre-history if you like.
[359.02s -> 363.66s]  So language modeling itself, that goes way back.
[363.66s -> 371.46s]  I mean, yeah, **Claude Shannon** 香农信息论之父 in 1950s talked about that.
<!-- 这句话就是 Language Modeling 的总结 -->
[371.50s -> 379.22s]  So it's about taking language and predicting the next token or next word each step.
[379.22s -> 384.50s]  And obviously that's the **free** TODO: 为什么称其免费？training mechanism we use for large language models.
[384.50s -> 389.06s]  And that's how they get their name where you're just trying to predict the probability
[389.06s -> 390.06s]  of these tokens.
[390.06s -> 399.62s]  We do this now on these massive corpora and pick up those probability distributions.
[399.66s -> 409.58s]  So in 2003, there's sort of one of the first methods for doing that with a neural network.
[409.58s -> 412.38s]  That's **Benjard du Charmen-Vincent 这三个人是 词向量的 作者**.
[412.38s -> 420.74s]  So they had word embeddings at the first layer and then various layers, 10H and softmax
[420.74s -> 424.22s]  to get the final prediction.
[424.22s -> 431.90s]  And I just put an interesting quote there in their conclusions that they say there's
[431.90s -> 436.14s]  probably a lot more to be done to improve the model, the architecture, computational
[436.14s -> 440.14s]  efficiency, 
<!-- 希望在不增加训练时间的基础上增加 capacity -->
and they'd like to increase the capacity without increasing training time
[440.14s -> 443.70s]  because they want to deal with corpora of hundreds of millions of words.
[443.70s -> 449.66s]  So that's kind of where we got to some years later.
[449.66s -> 451.38s]  Now that was 2003.
<!-- SVM 的研究： -->
[451.38s -> 456.26s]  Most of the 2000s actually, the research wasn't really focused on neural networks.
[456.26s -> 458.94s]  It was focused on support vector machines.
[458.94s -> 465.26s]  So these kernel classifiers, I worked in that area too, as you can see there's a
[465.26s -> 468.18s]  paper from me.
[468.18s -> 476.22s]  And it was kind of that, well, held back to the LLM story at least for a few years.
[476.22s -> 483.98s]  So here I have a slide from myself, **Renaud Colbert from 2008**, presented ICML where we
[483.98s -> 489.06s]  were trying to argue that the support vector machines of the day that were used
[489.06s -> 494.86s]  in these cascades of systems, parts of speech taggers and name density recognizers
[494.86s -> 498.22s]  and parsers, and it's not a good idea because we could train the whole thing end
[498.22s -> 501.94s]  to end with a neural network.
[501.94s -> 506.02s]  And no one was really doing that then.

<!-- Bengio 2003 指的是 《A Neural Probabilistic Language Model》
1. 也就是我之前觉得的深度学习的定义：word embedding && word model 一起学习
-->
[506.02s -> 513.10s]  So we had a paper at that time, Unified Architecture for NLP, which we considered
[513.10s -> 519.86s]  sort of the successor to the Bengio work from 2003 there.
[519.86s -> 527.54s]  So here what we did was we also had a neural network with word embeddings at the first
[527.54s -> 534.38s]  layer, then convolutional layers, max over time, which is a kind of proto-attention
[534.42s -> 536.62s]  and followed by a softmax.
[536.62s -> 543.82s]  And we showed that you could train this model as a sort of mass language model on
[543.82s -> 547.90s]  something like Wikipedia, which actually was pretty tricky at the time with the
[547.90s -> 551.94s]  computer we had, and it could learn some pretty interesting things like you could
[551.94s -> 554.46s]  see from the word similarities.
[554.46s -> 560.58s]  This is obviously pre-Worzavec, which I think was 2013, which is a simpler model,
[560.58s -> 560.86s]  right?
[560.90s -> 564.90s]  This is a more complex neural net that you could do that.
[564.90s -> 570.14s]  So you could pre-train on Wikipedia, and then afterwards you could fine-tune on tasks
[570.14s -> 577.06s]  of interest, like speech tagging, name density, chunking, SRL, and that worked.
[577.06s -> 585.82s]  So, yeah, this was kind of a predecessor to where we are today as well.
[585.86s -> 592.10s]  It was interesting because at the time that wasn't appreciated by everyone in the NLP
[592.10s -> 592.66s]  community.
[592.66s -> 598.06s]  So in the Stanford Natural Language Group, they had a reading group there where they
[598.06s -> 603.02s]  called it a bullshit ICML paper that was kind of on their public website.
[605.18s -> 610.30s]  And then this same paper won a Test of Time Award at ICML 2018.
[611.30s -> 618.38s]  And then Stanford University then opened the Center for Research on Foundation Models,
[618.38s -> 623.74s]  and their position paper called that same paper a prescient work.
[623.74s -> 628.10s]  So we kind of went from bullshit to prescient in that number of years, and
[628.10s -> 630.74s]  that's kind of how the field changed.
[630.74s -> 636.18s]  Of course, these papers—I've talked about just a few papers.
[636.18s -> 637.94s]  There's many, many papers, right?
[638.14s -> 640.42s]  They all build on each other.
[640.42s -> 648.66s]  I don't like to think of, you know, kind of like one paper that was the paper that
[648.66s -> 657.86s]  did something because, you know, all this work builds on top of the brilliant work
[657.86s -> 658.58s]  before.
[658.58s -> 665.14s]  But so I just show a few here of a timeline, though, of how these things went.
[666.14s -> 678.78s]  And yeah, the interesting thing is how fast the use of neural nets in NLP and machine
[678.78s -> 685.98s]  learning grew from this time from, say, 2008 to 2018.
[685.98s -> 691.46s]  So there was like four papers in ICML 2008 with the words deep or neural in them,
[691.54s -> 696.90s]  and I'm sort of co-author on two of them, and then there's like 100 in ICML 2018.
[696.90s -> 703.86s]  Obviously, this is a neural network based things are the majority today.
[705.14s -> 706.50s]  That's the **paradigm** of today.
[706.50s -> 710.98s]  Of course, can't say what's going to be in the future, but it's looking like a
[710.98s -> 712.18s]  pretty powerful approach.

[714.66s -> 721.18s]  Yeah, so of course we were interested in pushing this further and, you know, making
[721.22s -> 722.26s]  these models **reason**. TODO: 有更深刻的知识，推理能力，是和记忆能力相对应的能力

<!-- 开始让 ai 模型做阅读理解 -->
[722.26s -> 733.66s]  So in 2015, we devised this task, very simple task called the baby tasks, which,
[733.66s -> 740.14s]  yeah, ask these simple questions given little stories, but the neural nets of the
[740.14s -> 743.42s]  day, **LSTMs** TODO: 当时的几种技巧, actually couldn't solve them.
[745.50s -> 750.30s]  And so we were hoping that they could sort of spark innovation of new methods around
[750.30s -> 759.42s]  the same time the LLM attention mechanism was born in 2014, so the Bahdanau-Ocho-Benjio
[759.42s -> 759.90s]  paper. 
<!-- TODO: 提到的这个 paper
《Neural Machine Translation by Jointly Learning to Align and Translate》
解决了早期 Seq2Seq 模型在长句子翻译中的信息瓶颈问题
- TODO: blog-插入 attention 的热力图，attention 解决的也是一个匹配的问题，源语言-目标语言，只是这种匹配不解决排他，
- 有点像 jpda && GNN
- 这个 alignment 的对齐机制，是注意力机制的一个创新点
-->

[759.90s -> 767.98s]  So that was built for machine translation where the sort of you'd have attention
[767.98s -> 773.82s]  between the target sentence words and the source sentence words so that you could
[773.82s -> 778.62s]  have an **alignment** <!--目标语言做 Q，原始语言是 KV --> between the words in the two languages so you could translate
[778.62s -> 779.18s]  them. 
[779.18s -> 785.50s]  You can see this sort of attention map picture in the middle of the slide here.
[786.30s -> 794.46s]  So yeah, what we showed was that for these kind of baby reasoning tasks, if we
[794.46s -> 802.30s]  stack these layers of attention, then you can actually do multiple reasoning steps.
[802.86s -> 809.18s]  If you've got a question like, where is John here?
[809.18s -> 813.34s]  So, Daniel went to the bathroom, Mary traveled to the hallway, John went to the
[813.34s -> 818.46s]  bedroom, John traveled to the bathroom, Mary went to the office, where is John?
[819.90s -> 824.30s]  Then you could attend to these correct sentences to get that right.
[824.30s -> 828.22s]  Actually, that one's pretty easy because you only need to attend to John traveled to
[828.22s -> 829.50s]  the bathroom, the last sentence.
[830.14s -> 834.46s]  But then that's called one supporting fact question.
[834.46s -> 837.82s]  But then you have a **two supporting fact question** where it's a little trickier.
[837.82s -> 843.10s]  So there, John dropped the milk, John took the milk there, Santa went back to the
[843.10s -> 846.46s]  bathroom, John moved to the hallway, Mary went back to the bedroom.
[846.46s -> 848.14s]  And the question is, where is the milk?
<!-- 围绕推理能力，attention 怎么带来推理能力 -->
[848.86s -> 855.98s]  So now you have to see that the model will attend on like the first two layers.
[856.62s -> 859.74s]  You can see the attention scores here 
<!-- 这里的 hops 是 memory network 里面的概念，关注下面几篇文章
Memory Networks（Weston et al., 2014–2015）
后来演化为：
- End-to-End Memory Network
- Dynamic Memory Network
- 最终影响到 Transformer（multi-head self-attention, 多层堆叠）
感觉还是史前时代，并没有 attention 新
-->
in hop one, hop two, hop three.
<!-- blog-具体的例子，演示 attention 机制是怎么做推理的 -->
[860.30s -> 862.46s]  This is in the story two, two supporting facts.
[862.46s -> 865.98s]  You see it attends to the sentence, John took the milk there.
[865.98s -> 868.70s]  And so now it knows that John has the milk.
[868.70s -> 873.10s]  And then it can attend to this next sentence, John moved to the hallway in the further
[873.10s -> 877.50s]  layers of the neural network so that it can answer the hallway's correct answer.


[877.50s -> 884.54s]  So this was basically showing how in these very simple problems, the attention mechanism
[884.54s -> 889.90s]  when stacked layer by layer can give you more sophisticated reasoning.
[889.90s -> 894.14s]  And so this was built into this neural network at the time called the memory network.
[894.14s -> 898.22s]  So it had these stacked layers of attention, query and key embeddings, position embeddings,
[898.22s -> 904.70s]  so it knew which sentence or token was being attended to, neural networks between
[904.70s -> 906.94s]  the attention layers and the final softmax layer.
[907.98s -> 913.18s]  And so in many ways, it was a kind of predecessor to the transformer which
[913.18s -> 916.78s]  improved on this recipe with some other things like 
<!-- 这些当时新的 attention 的方式 和 memory bank 比较有什么不同？-->
- multi-headed attention,
- [916.78s -> 919.18s]  self-attention and 
- normalization.
[921.18s -> 927.82s]  And yeah, that led us to 2017 with the advent of the transformer.
[927.82s -> 931.82s]  And that's kind of more or less the architecture we're using today with some tweaks 小改动.

<!-- TODO: 其实到现在也没懂 masked 的价值在哪里，bert 的价值在哪里 -->
<!-- 时间线前进到 2018 -->
[931.82s -> 938.46s]  And then Bert in 2018 showed that a masked language model with a transformer could work very well.
[939.26s -> 950.70s]  And yeah, I just want to link that to 
<!-- 这篇 paper 的亮点：
1. 使用 LSTM RNN 实现 端到端的神经机器翻译 ：用两个 LSTM（编码器 + 解码器），将源语言编码成一个固定长度的上下文向量（context vector），再解码为目标语言序列。
2. 提出了将输入序列压缩为一个固定长度的向量，由解码器生成输出，引出了一个重要问题：长句子的信息压缩瓶颈，为注意力机制的提出铺路
3. -->
a paper from 2014 with Sutskever, Vinyals, and Quoc,
[952.46s -> 959.50s]  which was showing that you could do sequence to sequence learning with neural networks.
[959.50s -> 967.26s]  Now, I think that wasn't with attention maps yet, but still,
[967.82s -> 973.98s]  the conclusions from that paper were essentially the scaling hypothesis that we're using today.
[974.54s -> 976.54s]  So you can see this conclusion slide.
[976.54s -> 979.66s]  If you have a large big data set and you train a very big neural network,
[979.66s -> 981.50s]  then success is guaranteed. 什么大力出奇迹

[981.50s -> 982.38s]  It's a little bit glib（轻率的、肤浅的、油嘴滑舌的）.
[982.94s -> 989.26s]  But yeah, this scaling hypothesis, essentially when 
<!-- blog-可以放图 -->
Ilya Sitskyva went to OpenAI,
[989.26s -> 997.90s]  they drove this hypothesis, you know, making GPT-1, 2, 3, 4, and so on, right?
[1000.14s -> 1004.14s]  Bigger models, more data, and indeed this has worked.
[1004.14s -> 1010.06s]  So these are basically the ingredients that have taken us to some degree,
[1010.06s -> 1011.26s]  sort of LLMs everywhere.
<!-- blog-放图 -->
[1011.26s -> 1016.78s]  So I asked actually an LLM to give me a list of LLMs that have come out in year order.
[1016.86s -> 1022.06s]  This doesn't include all of them, but you can see a bunch that have come out here.
[1025.58s -> 1029.34s]  But you know, that's just so far been about,
[1030.86s -> 1034.30s]  mostly about language modeling and the language model objective function.
[1034.30s -> 1036.70s]  And that isn't actually enough.
[1036.70s -> 1040.06s]  So we do need other ways of training these models.
[1040.06s -> 1046.30s]  And I would characterize sort of 2020 onwards as exploring that more deeply.
[1046.38s -> 1048.14s]  Now we have these better language models.
[1050.46s -> 1059.66s]  So 2019, actually we did a work on dialogue agents, which we call the self-feeding chatbot,
[1059.66s -> 1064.30s]  where they could train not only just with this sort of language model objective,
[1064.30s -> 1069.10s]  but by using a reward model.
[1069.10s -> 1074.14s]  So we train a reward model, and then during conversations with humans,
[1074.94s -> 1079.66s]  if it thinks there's a large reward for one of the things it said,
[1080.22s -> 1085.82s]  it can add that back into the training set, and then do you supervised fine tuning
[1085.82s -> 1088.38s]  on this ever-growing data set.
[1088.38s -> 1101.26s]  So this was kind of a pretty simple version of what's being done today with RL-HAF and RL-AIF.
[1101.42s -> 1112.70s]  Then in 2020, we released this Blenderbot model that was a pre-trained language model
[1112.70s -> 1115.10s]  up to about 10 billion parameters.
[1115.10s -> 1122.22s]  And then crucially, we don't just use the language model pre-training objective.
[1122.22s -> 1126.78s]  We supervised fine tune that on dialogue data, which was human annotated.
[1127.50s -> 1138.22s]  And then when you evaluated this with humans, they actually said our best models were about
[1138.22s -> 1146.46s]  as engaging as the average human, and superior to another model from Google called Mina at the time.
[1149.66s -> 1155.74s]  But the actual recipes that we use today, we do use supervised fine tuning today.
[1156.06s -> 1158.86s]  But there's some more sophisticated stuff as well, right?
[1158.86s -> 1169.58s]  So in 2022, you had the instruct GPT paper, which advocated more for reinforcement learning
[1169.58s -> 1170.62s]  from human feedback.
[1170.62s -> 1176.62s]  So what you do there is you have this sort of SFT stage where you collect demonstration
[1176.62s -> 1179.34s]  data from humans, that's step one.
[1179.90s -> 1183.50s]  But step two, you also collect comparison data.
[1184.46s -> 1190.22s]  So which of these two responses is better, A or B, and then get humans to rank those.
[1190.22s -> 1191.82s]  And then you train a reward model.
[1192.54s -> 1197.10s]  So similar to how we had a reward model in the self-feeding chatbot.
[1197.10s -> 1203.90s]  But then you use reinforcement learning with that reward model to then kind of generalize
[1204.46s -> 1212.94s]  those comparisons with the reward model function to new generations from your policy.
[1213.50s -> 1221.26s]  And try and make your model better by generating responses and essentially judging
[1221.26s -> 1223.58s]  with this reward model and fixing itself, right?
[1223.58s -> 1233.50s]  So that's kind of more of a step towards this self-training kind of goal beyond the
[1233.50s -> 1237.02s]  language model training criterion.
[1238.94s -> 1242.06s]  And then there's sort of an alternative to RLHF.
[1242.06s -> 1248.54s]  Well, it's a little bit simpler called direct preference optimization I mentioned because
[1248.54s -> 1251.58s]  it's also pretty popular, DPO.
[1252.30s -> 1257.50s]  So it sort of says, okay, let's not use a reward model if we've got preference data.
[1257.50s -> 1265.26s]  We're just going to directly push the probability of the chosen in a preference pair sort
[1265.26s -> 1269.98s]  of up and the probability of the rejecting the preference pair.
[1269.98s -> 1273.66s]  So these would be two possible outputs from the model, push one up, push one down.
[1273.66s -> 1275.90s]  So there's a sort of a margin between the two.
[1277.18s -> 1285.98s]  And in certain experiments, the DPO works quite well compared to PPO, RLHF.
[1287.18s -> 1290.62s]  And then SFT can also work, but generally a little worse.
[1290.62s -> 1292.30s]  But it depends kind of on the setting.
[1292.86s -> 1302.86s]  And I think in some cases you really do need the full reinforcement learning because your
[1302.86s -> 1304.78s]  policy is going to change, right?
[1305.74s -> 1311.66s]  So the DPO just with a fixed preference data like that can't take that into account.
[1313.34s -> 1318.46s]  But we'll see ways of fixing that by making it iterative as well.
[1319.26s -> 1328.14s]  But overall, you choose one of those methods, SFT, RLHF, or DPO, and fine tune your language
[1328.14s -> 1332.22s]  model with one of them, and then you get pretty good instruction following.
[1332.22s -> 1336.86s]  So there isn't necessarily sort of this explicit chain of thought reasoning yet, but
[1337.66s -> 1342.22s]  compared to the original language models, you're doing really well.
[1342.22s -> 1347.10s]  So for example, here is from the instruct GPT paper, you've got this prompt, what's
[1347.98s -> 1355.26s]  the purpose of this code, GPT-3 without the sort of fine tuning doesn't do a very good
[1355.26s -> 1358.46s]  job, or instruct GPT does a much better job on the right-hand side.
[1359.18s -> 1366.62s]  So obviously, yeah, today we all know quite a lot about using these chat GPT type models
[1366.62s -> 1372.46s]  as we're mostly, yeah, a lot of the population is using them at this stage.
[1373.18s -> 1383.90s]  So, okay, that got me up to basically having a really good system one model, right?
[1383.90s -> 1389.10s]  It takes in this input, say this instruction, it directly spits out an output, but it
[1389.10s -> 1390.94s]  isn't doing the system two reasoning.
[1391.66s -> 1394.70s]  So that's kind of the next step.
[1394.70s -> 1404.78s]  And yeah, between say 2022 and 2023, the approach to doing that was what I would call
[1404.78s -> 1405.90s]  a prompting approach.
[1406.94s -> 1412.06s]  And so I'm gonna talk about those first, and then we're gonna look at more modern
[1412.06s -> 1419.42s]  things from the last year or so, where we're gonna more train directly to do this
[1419.42s -> 1420.86s]  system two reasoning instead.
[1420.86s -> 1430.38s]  So chain of thought prompting, the initial papers, they did that in a couple of ways.
[1430.94s -> 1435.50s]  One was by what's called few-shot prompting.
[1435.50s -> 1441.50s]  You would have say for some maths task, you would have examples of the kind of chain
[1441.50s -> 1443.58s]  of thought reasoning you would like to see.
[1443.58s -> 1451.58s]  So say if you had, I don't know, eight-shot examples, you'd have eight examples of doing
[1452.22s -> 1453.18s]  reasoning.
[1453.18s -> 1461.34s]  So it can be that's shown here, instead of just saying the answer is 11, as in standard
[1461.34s -> 1465.50s]  prompting, you would have broader started refiables, two cans of three tennis balls,
[1465.50s -> 1469.02s]  each is six tennis balls, five plus 60, because 11, the answer is 11, right?
[1469.02s -> 1473.26s]  So that's the chain of thought there that's highlighted.
[1473.58s -> 1478.94s]  So you'd have examples of that in the prompt, and now you would generate from the language
[1478.94s -> 1485.34s]  model, and it's going to mimic that few-shot prompting and use a chain of thought.
[1485.34s -> 1489.82s]  And so that was kind of one of the first approaches of prompting.
[1489.82s -> 1495.42s]  And then in the other paper here, large language models and zero-shot reasoners,
[1495.42s -> 1499.34s]  they showed actually you can be even simpler.
[1499.34s -> 1504.54s]  You could just say, let's think step by step in the prompt, and that could still bring
[1504.54s -> 1509.66s]  about these steps, these chains of thought could happen that it could generate before
[1509.66s -> 1511.10s]  it generates the final response.
[1512.46s -> 1517.82s]  And you get really big improvements on math tasks.
[1517.82s -> 1524.70s]  So you could go from, say, 10% on GSM 8K up to 40% or 50%.
[1525.66s -> 1535.82s]  So, yeah, that's kind of really spurred people to push the system two approaches further.
[1536.54s -> 1541.18s]  And it's not just math tasks that that works for.
[1544.06s -> 1549.90s]  So you can also look at the other failures of system one of the base language model.
[1550.62s -> 1555.18s]  It also has a factuality and hallucination issues, right?
[1555.18s -> 1560.62s]  So here's an example query, names and politicians who were born in New York, and the third
[1560.62s -> 1565.66s]  one it lists here, I think this is from chat GPT, is Michael Bloomberg, which is
[1565.66s -> 1566.22s]  incorrect.
[1568.30s -> 1575.34s]  So you can try and set up a system two reasoning type chain of thought to fix this problem.
[1575.34s -> 1576.86s]  So it's not a math problem, right?
[1577.42s -> 1585.34s]  So that's a paper we did called chain of verification, where the idea is you get this first
[1585.34s -> 1588.70s]  baseline response, you can think of that now as your draft.
[1588.70s -> 1592.14s]  So it's not actually your final response, it's part of your chain of thought.
[1592.14s -> 1600.14s]  And then given that draft, the language model asks itself more questions to sort
[1600.14s -> 1601.58s]  of check its own draft.
[1602.14s -> 1605.18s]  So it could ask, you know, where was Hillary Clinton born?
[1605.18s -> 1606.38s]  Where was Donald Trump born?
[1606.38s -> 1608.14s]  Where was Michael Bloomberg born?
[1608.14s -> 1611.82s]  And then answer those again as single questions.
[1611.82s -> 1619.50s]  Now the answer might be different than sort of writing out this whole list from the
[1619.50s -> 1624.06s]  names on politicians question, because it's sort of phrased differently, you actually
[1624.06s -> 1629.50s]  get a different response from the model, and models tend to be better actually at
[1629.50s -> 1637.26s]  these single question answer pairs that are short compared to these long kind of
[1637.26s -> 1641.90s]  responses they write, they're more likely to get something wrong somewhere in the
[1641.90s -> 1643.10s]  long response.
[1643.10s -> 1648.22s]  So when you plan those verifications of those verification questions and execute
[1648.22s -> 1652.06s]  them, you can actually get the model to see its own discrepancy.
[1652.06s -> 1656.86s]  So now it actually knows that Michael Bloomberg was born in Boston, even though
[1656.86s -> 1661.74s]  it's included him in the list of politicians who were born in New York.
[1661.74s -> 1668.86s]  And now you can make it kind of cross check itself and see that it was wrong and
[1668.86s -> 1674.62s]  write a final verified response and treat the old one as a draft.
[1674.62s -> 1676.38s]  And now it gets that correct.
[1677.18s -> 1685.82s]  So that's kind of, you know, a somewhat different chain of thought system to reasoning
[1685.82s -> 1687.18s]  compared to the math problems.
[1687.74s -> 1697.26s]  And yeah, in that work we showed that on various knowledge tasks, you can get large
[1697.26s -> 1703.10s]  performance in precision like three times as good with that approach.
[1704.94s -> 1713.34s]  So yeah, and you know, you could think, oh, that's sort of, maybe because that
[1713.34s -> 1720.06s]  paper was from a little while ago that, you know, might be fixed today.
[1720.06s -> 1725.74s]  But actually, I tried on chat GPT for, oh, and it's still making these kind of
[1725.74s -> 1726.22s]  mistakes.
[1726.22s -> 1732.62s]  Like here I did a query list 30 most famous women AI, and it included Joshua Benjio in
[1732.62s -> 1739.02s]  the list, or what prominent women work at OpenAI, and it said Ilia Sidskeverin as the
[1739.02s -> 1739.90s]  first in the list.
[1739.90s -> 1745.90s]  So, you know, still something that definitely needs to be fixed, and you can
[1745.90s -> 1748.54s]  fix it with this sort of system to reasoning.
[1749.10s -> 1752.14s]  I think actually 01 does better.
[1754.06s -> 1754.30s]  Yeah.
[1757.90s -> 1762.30s]  Yeah, and there's other things you can do with the system to reasoning as well.
[1763.10s -> 1769.74s]  So here's another problem with language models that they have what's called
[1770.70s -> 1773.58s]  semantic leakage and sycophancy.
[1773.58s -> 1780.54s]  So when you do attention, because it's a soft attention, it's not sharp.
[1781.26s -> 1785.50s]  You know, you're assigning probabilities across the context.
[1786.30s -> 1792.30s]  So there'll be all these sort of non-zero values, and it means the whole context
[1792.30s -> 1794.38s]  can affect the LLM output.
[1794.38s -> 1802.70s]  And this can be bad because, you know, even basically we see irrelevant parts which look
[1802.70s -> 1806.14s]  sort of superficially correlated tend to have an effect.
[1806.70s -> 1813.18s]  So, for example, a prompt like he likes ants, his favorite food is can get completed
[1813.18s -> 1818.30s]  by the language model was ant covered chocolate, which, you know, isn't particularly desirable.
[1818.30s -> 1819.02s]  He likes yellow.
[1819.02s -> 1821.18s]  He works as a school bus driver.
[1821.74s -> 1825.98s]  That's from Ganon et al in 24.
[1828.46s -> 1831.74s]  So I see this is a similar problem, the sycophancy problem.
[1831.74s -> 1836.62s]  If you say something like as an instruction, I think that the sun is yellow when viewed
[1836.62s -> 1838.14s]  from space, what do you think?
[1838.14s -> 1844.86s]  So you kind of prime with the wrong answer because actually that's an illusion caused
[1844.86s -> 1845.74s]  by atmosphere.
[1846.86s -> 1850.78s]  Then it will actually agree, the LLM tends to agree with you.
[1851.58s -> 1855.18s]  And say, yes, the sun is actually yellow when viewed from space.
[1855.90s -> 1860.46s]  So I sort of see that as a similar problem that basically you've got that text in the
[1860.46s -> 1865.18s]  context and it tends to attend to it and get things wrong.
[1865.18s -> 1870.14s]  So another example, if you add some facts about some city in the context like Sunnyvale
[1870.14s -> 1875.34s]  and then you ask for someone's birthplace, it's likely to say Sunnyvale is the answer.
[1875.34s -> 1881.42s]  So yeah, I just typed in this one today.
[1881.98s -> 1886.22s]  Did OpenAI have a model called self-feeding at one time?
[1886.22s -> 1892.22s]  And it replied, yes, OpenAI introduced the concept of self-feeding in the self-feeding
[1892.22s -> 1895.98s]  chatbot paper, which, you know, that wasn't actually from OpenAI.
[1895.98s -> 1898.54s]  That was from Facebook AI research.
[1898.54s -> 1900.86s]  So again, you can still prime these.
[1900.86s -> 1903.90s]  You know, this is a sort of current day problem.
[1904.86s -> 1907.18s]  So how can you fix that with system two reasoning?
[1907.18s -> 1916.70s]  So there was a paper called system two attention we did last, that was, yeah, end of 2023,
[1916.70s -> 1926.06s]  I think, where you do this chain of thought reasoning, which attempts to rewrite the
[1926.06s -> 1928.54s]  original instruction and remove the bias.
[1928.54s -> 1930.38s]  So again, this is done by prompting.
[1930.38s -> 1933.42s]  So essentially the prompt is to give the original instruction.
[1934.06s -> 1940.14s]  And then ask the language model, rewrite this instruction, remove the irrelevant parts and
[1940.14s -> 1943.10s]  the bias, and then you'll get a new instruction.
[1943.10s -> 1947.34s]  And then you get the language model to answer the rewritten instruction, right?
[1947.34s -> 1952.46s]  So you want to get rid of this bias and then you can get better results.
[1952.46s -> 1955.26s]  You're not biased as much by this issue.
[1955.26s -> 1959.90s]  So for example, I think the sun is yellow when viewed from space.
[1959.90s -> 1960.86s]  What do you think?
[1960.86s -> 1967.34s]  When you use this sort of chain of thought system two attention to rewrite that, it would
[1967.34s -> 1970.78s]  rewrite it as, I'm curious about the color of the sun when viewed from space.
[1970.78s -> 1973.18s]  Can you provide information on this topic?
[1973.18s -> 1979.82s]  So to remove the yellow, which was kind of, you know, biasing the question to a certain
[1979.82s -> 1980.32s]  answer.
[1981.34s -> 1984.54s]  And yeah, this works also on math problems.
[1984.62s -> 1993.98s]  If there's like, say, parts, there's parts of the math problem which are completely irrelevant,
[1993.98s -> 1999.58s]  they can actually fool a model and it will try and remove those.
[2001.10s -> 2008.54s]  So yeah, this is, yeah, just to show you really that chain of thought and system two
[2008.54s -> 2010.22s]  reasoning, it's not just for math problems.
[2010.22s -> 2016.94s]  There's like a lot of things a model can think about with these intermediate tokens
[2016.94s -> 2022.30s]  and fix a lot of problems in all kinds of tasks it's trying to solve.
[2023.50s -> 2026.94s]  This last one I show, it's the task with evaluation.
[2026.94s -> 2032.62s]  So you're given a question like an instruction and two possible responses.
[2032.62s -> 2036.86s]  You want the model to say which of the two responses is better, which is a really
[2036.86s -> 2043.50s]  important thing for training, as we show, because you could basically use that as a
[2043.50s -> 2044.22s]  reward model.
[2044.86s -> 2047.10s]  And it's also important for evaluation as well.
[2047.66s -> 2051.42s]  But yeah, you can also do system two reasoning there.
[2051.42s -> 2058.54s]  So in this paper branch solve merge, the way that was done was, again, through prompting
[2059.10s -> 2067.42s]  by asking, given that instruction, to first ask the language model to break down its
[2067.42s -> 2073.10s]  evaluation into different criteria such as relevance, clarity, accuracy, originality,
[2073.10s -> 2079.18s]  and it would come up with those criteria specific to the task that it's trying to
[2079.26s -> 2088.70s]  solve, and then to generate an evaluation independently for each of those different
[2088.70s -> 2091.66s]  branches and then merge them back together again.
[2091.66s -> 2096.94s]  And it was shown that that could give better evaluation results through the extra
[2096.94s -> 2099.90s]  thinking time, basically, that the language model has.
[2101.82s -> 2107.42s]  So yeah, there's many other works as well during that period.
[2107.50s -> 2113.98s]  But I just wanted to kind of give an overview of a few of them to show there was a lot of
[2113.98s -> 2118.78s]  prompting approaches that showed that spending time thinking could get you better
[2118.78s -> 2119.26s]  results.
[2120.46s -> 2128.22s]  But what we really want to do is try and train these models end to end to be able
[2128.22s -> 2131.50s]  to be good at reasoning, not like just prompting, right?
[2131.50s -> 2139.66s]  So I'd say the next wave after that is, and we're in it right now, is improving this
[2139.66s -> 2144.86s]  reasoning through optimization, and so better reasoning via self-improvement.
[2147.74s -> 2154.62s]  And to get there, I'm going to start with the self-rewarding language models I was
[2154.62s -> 2157.90s]  talking about right at the beginning of the talk.
[2158.78s -> 2165.82s]  And so this is a method where LLM improves itself by assigning rewards to its own outputs
[2167.34s -> 2170.14s]  and optimizing itself.
[2170.78s -> 2179.98s]  So yeah, where the hope is that this could lead to it becoming smarter at each iteration.
[2180.86s -> 2188.86s]  And yeah, so the research question is, can that make it superhuman?
[2191.42s -> 2197.02s]  So the standards reinforcement learning from human feedback, which I mentioned earlier
[2197.02s -> 2203.42s]  in the talk, uses humans in the loop first to create the supervised fine-tuning data,
[2203.42s -> 2208.78s]  so the instructions and their responses, and then to collect these judgments, so which
[2209.34s -> 2211.42s]  of these two responses is better, A or B?
[2212.70s -> 2218.54s]  Now, yeah, that's shown in this picture that I showed before.
[2218.54s -> 2224.94s]  So there's two spots where there's a human, and the problem is language models are
[2224.94s -> 2226.54s]  getting better and better, right?
[2226.54s -> 2237.02s]  So it's just getting a really tricky job for humans to be as good as we need for
[2237.02s -> 2237.82s]  these tasks.
[2237.82s -> 2243.02s]  Humans need to read these responses really carefully in order to make decisions.
[2244.06s -> 2253.58s]  So for example, now that our LLMs are really good at writing code or no sophisticated
[2256.14s -> 2261.82s]  math outputs, even getting good at like, I mean, maybe not perfect yet, but getting
[2261.82s -> 2266.22s]  good at legal or medical outputs, things like this, the problem is it's harder and
[2266.22s -> 2270.62s]  harder for humans to be good labelers for these tasks, right?
[2270.62s -> 2278.54s]  You might need some of the best mathematicians, human mathematicians in the world to label
[2278.54s -> 2281.02s]  whether these responses are correct or not, right?
[2281.02s -> 2286.06s]  And similarly, you need really good coders, or even if you don't need them today, you'll
[2286.06s -> 2288.06s]  certainly need them tomorrow, right?
[2288.06s -> 2293.74s]  And so the average human that you pick from the population, then they're just not
[2293.74s -> 2298.30s]  going to be good enough at these specialized tasks and be able to annotate this data.
[2299.26s -> 2306.46s]  So this is what motivates trying to get the language model to try and help itself.
[2307.42s -> 2313.66s]  And so that's basically, otherwise, how can we continue improving a model if it's already
[2315.50s -> 2318.70s]  fairly superhuman compared to the average human that you could pick?
[2319.66s -> 2322.94s]  So there's two observations that can help us solve this.
[2323.90s -> 2329.98s]  Observation one is that we know language models can continue improving if they're given
[2329.98s -> 2334.54s]  good judgments on response quality, because that's what we're shown in reinforcement
[2334.54s -> 2338.78s]  learning from human feedback, or in something like DPO as well, right?
[2338.78s -> 2343.98s]  So if you have good preferences of chosen and rejected pairs, then you can improve
[2343.98s -> 2347.34s]  the model by training and pushing up the probability of the chosen.
[2347.90s -> 2350.46s]  And down the probability of the rejected.
[2350.46s -> 2356.30s]  The same thing for a reward model with reinforcement learning.
[2357.26s -> 2363.82s]  And observation two is that we actually have now language models that can provide good
[2363.82s -> 2365.34s]  judgments on model generation.
[2365.34s -> 2369.58s]  So I was showing you the branch-solve-merge approach just earlier.
[2369.58s -> 2376.38s]  So that's an approach for a language model, basically, to give a judgment on two
[2376.38s -> 2381.26s]  responses as an instruction-following task.
[2381.26s -> 2390.70s]  So this is called LLM as a judge, typically, where for the language model, it's not any
[2390.70s -> 2395.74s]  different a task than all the other instruction-following tasks it has to do, like write
[2395.74s -> 2399.98s]  some code or respond to this particular question.
[2399.98s -> 2405.18s]  And in particular, this question we're asking is which of these two responses better, A or B?
[2405.98s -> 2412.38s]  And there's a bunch of work showing LLM as a judge is actually a pretty good method.
[2412.38s -> 2415.42s]  So how about combining these two things together, right?
[2415.42s -> 2420.22s]  So we replace the human feedback with the LLM feedback.
[2421.74s -> 2426.86s]  So the key idea then is to train this so-called self-rewarding language model that
[2426.86s -> 2430.14s]  it's going to be its own judge as it's training.
[2430.14s -> 2435.10s]  So it needs to have this instruction-following capability for all the kinds of user
[2435.10s -> 2442.30s]  instructions we want, but one of those user instructions is actually the evaluation
[2442.30s -> 2443.90s]  task that we're interested in.
[2443.90s -> 2445.10s]  So it looks like this.
[2445.10s -> 2446.30s]  Here's an instruction.
[2447.10s -> 2449.02s]  Here is a model of response.
[2449.02s -> 2455.02s]  And then the task is can you assign a score, say, between 0 and 5, or the other ways
[2455.02s -> 2459.10s]  of doing that as well, but to this response and then based on some some rubric.
[2459.58s -> 2463.66s]  And then you would expect, say, a chain of thought reasoning process and then a final
[2463.66s -> 2465.82s]  judgment of the score of the response.
[2466.46s -> 2472.70s]  So if we have these two things, then we can make this model train itself and be
[2472.70s -> 2473.66s]  self-rewarding.
[2473.66s -> 2481.02s]  So we also go through iterative process of data creation and curation so that we close
[2481.02s -> 2484.38s]  this whole training loop where we train on this new data.
[2485.34s -> 2489.82s]  And then the goal is the model is going to get better in terms of both instruction
[2489.82s -> 2494.94s]  following and evaluation ability in each cycle.
[2494.94s -> 2498.06s]  And we empirically showed that that was possible.
[2498.06s -> 2501.18s]  So this was right at the beginning of last year.
[2503.18s -> 2508.30s]  So that was the picture that I was showing right at the beginning of the talk.
[2508.62s -> 2518.70s]  So, yeah, we did these experiments on LAMA 270B, and we used Open Assistant as a sort
[2518.70s -> 2519.50s]  of seed.
[2519.50s -> 2521.34s]  So that's seed instruction data.
[2522.54s -> 2525.74s]  And it also has some seed evaluation data.
[2527.50s -> 2532.62s]  So the LLM as a judge prompt that we use looks like this.
[2532.70s -> 2541.18s]  So that's asking it to do chain of thought and then score out of five a particular
[2541.18s -> 2541.68s]  instruction.
[2543.42s -> 2546.86s]  And then we're going to go through this training loop.
[2546.86s -> 2552.22s]  So the first part is it's going to generate new tasks.
[2552.86s -> 2556.78s]  So we use something called self-instruct to do that.
[2557.66s -> 2567.18s]  So basically you start with your seed instructions, which are from humans, and you use few-shot
[2567.18s -> 2571.98s]  prompting with a few of those instructions to ask the language model to generate a new
[2571.98s -> 2572.54s]  instruction.
[2573.50s -> 2578.46s]  And then you can do this hundreds of thousands of times to get a whole new set of tasks.
[2579.26s -> 2582.86s]  Then for those tasks, you can generate responses.
[2582.86s -> 2588.86s]  So you'll generate multiple candidate responses for each prompt or task.
[2588.86s -> 2591.18s]  So let's say four in our case.
[2591.74s -> 2596.94s]  And then you generate rewards with the LLM as a judge prompt that I just showed to
[2596.94s -> 2599.74s]  give you those scores for each of the four responses.
[2600.30s -> 2603.10s]  And from that, you can generate preference pairs.
[2603.10s -> 2608.78s]  You take the highest scoring of the four responses, and that would be the chosen for
[2608.78s -> 2611.50s]  DPO, and the lowest scoring would be the rejected.
[2611.50s -> 2618.14s]  You can carry on training your model now with this DPO training, and then repeat the whole
[2618.14s -> 2618.62s]  cycle.
[2618.62s -> 2625.18s]  Now you have a better model, MT plus one, you can go back, generate new prompts, generate
[2625.18s -> 2628.06s]  new responses, generate new rewards, and so on.
[2628.06s -> 2633.02s]  And we do this loop like three times in the experiments in that paper.
[2633.02s -> 2638.94s]  And we're going to evaluate the performance on two axes, the ability to follow instructions
[2638.94s -> 2640.94s]  and its ability as a reward model.
[2641.98s -> 2649.02s]  There's some benchmarks called alpaca eval 2, an empty bench at the time that we used
[2649.02s -> 2651.42s]  and another test set of prompts.
[2653.02s -> 2660.14s]  And we use GPT-4 evaluation and human evaluation to check how this model performed through
[2660.14s -> 2662.78s]  the three iterations of self-rewarding.
[2662.78s -> 2669.98s]  And you can see that they agree with each other, humans and GPT-4, that we compare
[2669.98s -> 2675.34s]  it to doing supervised fine-tuning on each iteration, the model's getting better.
[2675.34s -> 2678.62s]  So, it's getting better than the SFT baseline.
[2680.86s -> 2684.94s]  And yeah, so that's the sort of power of this self-training.
[2686.46s -> 2690.22s]  And we can look at the win rate on alpaca eval 2.
[2691.02s -> 2697.50s]  And this paper got quite a bit of attention at the time because this win rate for such
[2697.50s -> 2700.14s]  a sort of simple model was quite good.
[2700.70s -> 2707.34s]  It started from this llama 70b and the win rate went up from 10% to 15% to 20% in the
[2707.34s -> 2712.54s]  three iterations, which put it almost on par with GPT, a version of GPT-4.
[2714.22s -> 2721.66s]  And this was kind of just done by, the first author is Wei Zhe Yuan, he's a PhD
[2721.66s -> 2722.70s]  student at NYU.
[2722.70s -> 2728.54s]  So, it wasn't like a big team building this project, but the algorithm works quite well.
[2730.46s -> 2735.18s]  And yeah, so you could look at what it's actually improving at.
[2735.18s -> 2744.38s]  And it does improve on all kinds of skills, but particularly more things like humanities,
[2744.38s -> 2748.46s]  extraction, stem role-playing, writing, more than it improves, let's say, something like
[2748.46s -> 2749.58s]  math code and reasoning.
[2750.14s -> 2755.74s]  And the reason why that would be is because the LLM as a judge might not be as good at
[2755.74s -> 2759.74s]  evaluating math code and reasoning, and so it's harder for it to improve on those.
[2762.14s -> 2768.62s]  This is a breakdown, you have these topics, you can see that the gap between the iterations
[2768.62s -> 2771.18s]  is smaller for things like math, which is on the far right.
[2773.58s -> 2778.70s]  And then you can measure the ability of this model as an evaluator.
[2779.34s -> 2787.18s]  And one way of measuring that is by looking at its correlation with human judgments.
[2787.18s -> 2791.50s]  So, the pairwise accuracy, we had a whole bunch of metrics, but the pairwise accuracy
[2791.50s -> 2799.50s]  metric would show its agreement with humans on whether A or B are the right way around
[2799.50s -> 2800.70s]  or the wrong way around.
[2800.70s -> 2805.66s]  And you can see that it does increase, not by a massive amount, but it does increase
[2805.66s -> 2807.58s]  over the three iterations.
[2807.66s -> 2813.50s]  So, it is actually getting better at being a reward model, which I think is exciting,
[2813.50s -> 2820.30s]  because if the model is getting better at making judgments of what's right or wrong,
[2820.30s -> 2825.58s]  then it's getting better at rewarding itself following instructions.
[2825.58s -> 2828.54s]  So, there's kind of a virtuous circle going on there.
[2828.54s -> 2834.54s]  To some extent, of course, it plateaus in experiments, but still, it still gives it
[2834.54s -> 2842.22s]  the capacity to self-train and to get better than the initial human annotations that it
[2842.22s -> 2843.02s]  had at the beginning.
[2844.54s -> 2849.58s]  Now, as I said, it didn't improve as much on reasoning tasks.
[2849.58s -> 2855.26s]  So, the next thing we wanted to ask was how can we make it improve on those?
[2855.26s -> 2863.66s]  And yeah, so in April last year, we did this work called iterative reasoning preference
[2863.66s -> 2872.54s]  optimization, which I can see from the picture, it's a similar pipeline, but now we're going
[2872.54s -> 2873.90s]  to generate chain of thoughts.
[2873.90s -> 2877.98s]  So, in the experiments I just showed you, there were no chain of thoughts, right?
[2877.98s -> 2881.90s]  It was just kind of a system one language model output the answers for instruction
[2881.90s -> 2882.40s]  following.
[2883.66s -> 2889.34s]  But in this version, we're going to generate chain of thoughts and then answers, and we're
[2889.34s -> 2894.70s]  going to compute rewards, and otherwise, the pipeline is the same.
[2895.42s -> 2901.74s]  Now, the rewards aren't going to be done by LLM as a judge, because we don't trust
[2901.74s -> 2907.42s]  the LLM on these, say, these math tasks as much.
[2907.42s -> 2914.22s]  I mean, I think that's a subject of research, how can we get them to improve by trusting
[2914.22s -> 2915.18s]  their own judgments?
[2915.18s -> 2921.02s]  But in this work, we just said, okay, we've got a bunch of math training data where we
[2921.02s -> 2924.22s]  know the right answer, so let's just use that as a reward.
[2924.78s -> 2933.42s]  And this is being commonly called in the last weeks is like a verifiable reward for
[2933.42s -> 2935.02s]  a math problem, right?
[2935.02s -> 2942.06s]  So, what we're going to do is we're going to generate the chain of thought and then
[2942.14s -> 2948.30s]  the final answer, and then we're going to extract the final answer from the LLM response.
[2948.30s -> 2952.14s]  So, sort of remove the chain of thought part, just get the final answer, and then just
[2952.94s -> 2957.18s]  do a match with the answer that we know for the math problem.
[2957.18s -> 2961.98s]  So, you can do that with this kind of prompt, where you give the LLM the prompt.
[2961.98s -> 2966.06s]  Your task is to answer the question below, give step-by-step reasoning, and when you're
[2966.06s -> 2968.86s]  ready, please use the format final answer colon.
[2969.74s -> 2975.42s]  So, then you can just simply do this heuristic extraction where you search for final answer
[2975.42s -> 2980.38s]  colon, grab the text afterwards, that should be your answer, and now just do a string
[2980.38s -> 2986.78s]  match or some other fairly simple match with the answer, the known gold answer.
[2987.82s -> 2997.66s]  And that's how you can build your DPO pairs and improve your model, and then again,
[2997.66s -> 3001.90s]  iterate round, and that's the iteration again is important because now we've got a better
[3001.90s -> 3005.90s]  model answering these math problems, we're going to generate new chain of thoughts
[3005.90s -> 3009.58s]  with a better model, compute the rewards, and go round in a loop.
[3011.58s -> 3019.90s]  And we showed on math problems like GSM 8K that that's working really well.
[3020.86s -> 3025.58s]  So, yeah, you can see these improvements across iteration one to four.
[3025.58s -> 3034.54s]  It's gaining a little bit less than 10 percent there, and also improves on some
[3034.54s -> 3039.90s]  multi-choice problems on ARC challenge and on these harder math problems as well.
[3042.94s -> 3049.58s]  And yeah, we just showed that the DPO training is really important.
[3049.58s -> 3053.50s]  You can't just use supervised fine tuning with this training.
[3053.50s -> 3058.62s]  You really need the negative examples to be pushed down, otherwise it doesn't work.
[3061.66s -> 3068.38s]  And yeah, so in 2024, September or so, OpenAI's 01 came out.
[3068.38s -> 3072.38s]  Of course, the exact method is unknown.
[3072.38s -> 3077.58s]  They didn't publish a paper about it, but they did have, well, they didn't even show
[3077.58s -> 3081.34s]  the chain of thoughts either. From the model, there was a summary of the chain of thoughts.
[3081.34s -> 3087.18s]  I think they still do that, but it was capable of answering some quite sophisticated
[3087.98s -> 3092.54s]  reasoning math problems. And everyone was wondering, how did they do it?
[3092.54s -> 3099.58s]  Did they use some kind of process reward model that was evaluating the in-between steps?
[3099.58s -> 3105.50s]  Did they use MCTS or some really sophisticated search mechanisms to train
[3105.50s -> 3112.30s]  with reinforcement learning? Or a lot of ideas were posted on Twitter of how they do this.
[3113.02s -> 3123.18s]  And then DeepSeek 01 came out just this January, and Mark Chen from OpenAI tweeted,
[3123.18s -> 3127.42s]  congrats to DeepSeek on producing 01 level reasoning model. Their research paper
[3127.42s -> 3132.22s]  demonstrates they've independently found some of the core ideas that we did on our way to 01.
[3132.78s -> 3139.10s]  Okay, so then that means assuming that OpenAI used the same stuff as DeepSeek,
[3139.10s -> 3147.74s]  we have a DeepSeek paper so we can look at what they did. And in some respects,
[3147.74s -> 3153.74s]  it's quite similar to the iterative reasoning preference optimization that we did earlier in
[3154.30s -> 3160.70s]  2024 that I just showed you. So they have a prompt which asks it to think,
[3161.66s -> 3168.14s]  and then to put the answer in a box. You see this answer here in the prompt,
[3168.14s -> 3175.58s]  and then they extract that. And then they use a rule-based verification of correctness
[3176.54s -> 3183.02s]  with verifiable rewards, and they apply that in the loop, generating chain of thoughts,
[3183.02s -> 3187.42s]  checking just the correctness of the answer, and then rewarding this correctness.
[3187.42s -> 3195.74s]  They use a different optimization technique. They don't use iterative DPO, they use GRPO.
[3196.30s -> 3204.78s]  But otherwise, this recipe looks kind of like that. It's just done at much bigger scale.
[3204.78s -> 3208.94s]  So in the experiments I showed you, we just had like one data set like GSM 8K.
[3209.50s -> 3216.54s]  So a key here is start from a really strong big model. I think it's a 600 and something
[3216.54s -> 3225.74s]  parameter model, right? 671 billion parameter model, DeepSeek 3. And then you have a large
[3225.74s -> 3234.22s]  amount of this reasoning data with verifiable rewards, and you train with this RL generating
[3234.86s -> 3240.30s]  chain of thoughts and rewarding the ones that it gets right and basically exploring the space
[3240.30s -> 3246.22s]  of chain of thoughts. And they observe that the chain of thoughts get longer over training as
[3246.22s -> 3252.06s]  it finds sort of more sophisticated reasoning techniques. And then the final model does
[3253.26s -> 3257.98s]  very well on these code and math problems similar to OpenAI's 01 model.
[3258.94s -> 3265.74s]  You know, this actually was a big, big news outside of AI. You can see that NVIDIA's,
[3266.94s -> 3273.02s]  these articles here on Bloomberg, NVIDIA's DeepSeek drop as Wall Street fixated and
[3273.02s -> 3278.54s]  with their stock plunging and stuff like that. So it was a surprisingly big splash.
[3280.70s -> 3286.70s]  And then you have a couple of examples here of the chain of thoughts that it does.
[3287.50s -> 3292.30s]  The one on the left is from their paper. It's generating this answer to this question.
[3292.30s -> 3295.74s]  And then in the middle of it, like the chain of thought, it says, wait, wait, wait, that's
[3295.74s -> 3300.70s]  an aha moment I can flag here. Let's reevaluate this. And it starts saying some
[3300.70s -> 3307.74s]  other stuff. So they were just showing how it learns to rethink and, you know, fix its own
[3307.74s -> 3313.02s]  mistakes. And that was all done just with this, you know, this training that just rewarding
[3313.02s -> 3318.70s]  the final answer. And it was doing the rest itself. And I personally love the simplicity
[3318.70s -> 3323.26s]  of it that we didn't have to do, you know, really complicated things in the middle. It's
[3323.26s -> 3329.34s]  just, you know, just rewarding the end. And you can already get these impressive results.
[3329.34s -> 3336.30s]  So the one on the right is kind of a more funny one. Ask DeepSeek to select a random number.
[3336.30s -> 3343.98s]  And it outputs this large amount of a chain of thought where it sort of over thinks itself.
[3343.98s -> 3347.82s]  Maybe I should go with something like 777, but that's four sevens. It might be too
[3347.82s -> 3354.14s]  obvious. Alternatively, 123, too sequential. What about if I close my eyes and 42. Wait,
[3354.14s -> 3359.50s]  no, that's from Hitchhiker's Guide and so on. So it's pretty amusing what it ends up doing.
[3359.50s -> 3368.46s]  But yeah, almost a little human in a way, though. But I don't think that's actually
[3368.46s -> 3378.94s]  the way we really want to generate random numbers, obviously. Yeah, so from my own team's
[3378.94s -> 3390.06s]  work before that came out, so 2024 October, we were looking to extend our chain of thought
[3390.06s -> 3394.46s]  training results from iterative reasoning preference optimization. We share that work
[3394.46s -> 3399.18s]  quite well with math problems, but we want chain of thought reasoning for all problems, right?
[3400.06s -> 3411.02s]  Like even if you're thinking about how to write a poem, you might do a whole bunch of
[3411.02s -> 3416.14s]  thinking, write some drafts, try and understand what you're going to write about before you
[3416.14s -> 3423.34s]  actually write it. Just to pick an example that's very different to the math. So we
[3424.14s -> 3431.90s]  try to follow the same recipe. So we have a generic prompt just to initialize
[3432.70s -> 3439.74s]  the model, and we ask it to respond to whatever generic query, but do it in a
[3439.74s -> 3445.66s]  comprehensive and detailed way by writing your internal thoughts. And then you must include this
[3445.66s -> 3452.70s]  draft response and its valuation. And after you write your final response, have this special tag.
[3452.70s -> 3457.98s]  So again, that's so we can extract the response out and separate it from the thoughts.
[3460.14s -> 3466.06s]  And this is the same trick that we did before, and the same trick that DeepSeek does. But here
[3466.06s -> 3470.30s]  we're going to do it not on math problems, but on all kinds of other instruction following
[3470.30s -> 3477.82s]  problems. But now we won't have a verifiable reward anymore, but we still have these LLMs
[3477.82s -> 3483.98s]  as a judge that we were using in self-rewarding. So we can use that on the response to judge
[3483.98s -> 3490.46s]  whether the response is good, but the difference between this and the original self-rewarding work
[3490.46s -> 3498.14s]  is that we have the chain of thought generation before it. So we tried this and actually ended up
[3498.14s -> 3504.78s]  working quite well. It gave gains on alpaca eval and another benchmark called arena hard. It's
[3504.78s -> 3512.38s]  actually third on the alpaca eval leaderboard, I think at the time, and it was the best
[3512.94s -> 3518.46s]  eight billion parameter model on arena hard. I think one interesting thing about the training,
[3518.46s -> 3523.66s]  so again, we're doing this iterative training with DPO, is that so this is called
[3527.10s -> 3532.38s]  thought preference optimization, TPO. And we compare it to the direct baseline in this graph
[3532.38s -> 3539.18s]  in the bottom right, which is basically no chain of thought. And you can see in the first iterations
[3540.38s -> 3546.62s]  TPO actually makes the model a lot worse. And that's because these language models,
[3546.62s -> 3556.14s]  so we're using like llama3 eight billion, they're already really well fine-tuned
[3556.70s -> 3563.10s]  to be good without the chain of thought. So that kind of had a massive advantage over trying to
[3563.10s -> 3568.86s]  make it to the chain of thought, but after we train it on successful chain of thought
[3570.54s -> 3579.42s]  outcomes using the LLM as a judge or the reward model, then you can see that the gap closes
[3579.42s -> 3584.14s]  and then it starts improving on iteration three and four, and now it's better than the direct baseline.
[3585.02s -> 3592.46s]  So yeah, so I think this was really promising because it showed you could do this chain of
[3592.46s -> 3597.58s]  thought training, not just for math problems or verifiable tasks, but for anything, right?
[3599.82s -> 3609.26s]  And yeah, so here's a couple of examples of things it does. So you can say for a query,
[3609.26s -> 3616.94s]  write me a poem or what dog breed is smallest, it's going to do a whole bunch of thinking,
[3616.94s -> 3623.18s]  like draft responses and evaluation or various thought processes before it gets the output.
[3624.30s -> 3633.10s]  Yeah, and then DeepSeek R1 in their paper, not 100% sure if it's doing something the same as
[3633.10s -> 3638.14s]  what we're doing there with TPO, but there's a hint it is because it says
[3638.78s -> 3643.18s]  here are highlighted for general data, we resort to reward models to capture
[3643.18s -> 3650.70s]  human preferences in complex and nuanced scenarios. So I think they're also generating
[3650.70s -> 3656.30s]  chain of thought and then doing that, but it wasn't like fully spelled out in their paper,
[3656.30s -> 3664.94s]  so it wasn't completely clear. Yeah, and then there's other things we can do. So these,
[3665.66s -> 3670.38s]  as far to my knowledge, aren't actually yet in these bigger models, so these are more just like
[3671.50s -> 3675.98s]  research papers that hopefully then get scaled up to these bigger models.
[3677.66s -> 3685.66s]  The next work we did to try to show that the language model so far we've shown
[3685.66s -> 3689.90s]  it's quite good at improving its instruction and reasoning ability,
[3690.70s -> 3699.34s]  but we also want to explicitly improve its ability to evaluate itself. Because if we can do that,
[3699.34s -> 3705.10s]  then when it's doing these judgments, it's doing these reward model judgments,
[3705.10s -> 3708.22s]  it's going to get better at everything, right? It's going to get better instruction following
[3708.22s -> 3714.70s]  as well. So this work is called meta rewarding language models, where it's going to try to
[3714.94s -> 3721.18s]  improve its own judgments by meta judging its judgments. So obviously a little bit meta this
[3722.38s -> 3729.50s]  work. But so yeah, now you can sort of see the language model in three roles as an actor,
[3729.50s -> 3735.82s]  so following instructions as a judge, judging responses to those instructions, and as a meta
[3735.82s -> 3742.54s]  judge, it's going to judge its own judgments. And I'll show you how you can do that. We call
[3742.54s -> 3751.58s]  that LLM as a meta judge. So there's a prompt for that. So you'd have a given instruction from the
[3751.58s -> 3760.38s]  user, a response from say a model, and then judgment A and judgment B, which could include
[3760.38s -> 3767.26s]  the chain of thought and the final verdict. And then you want the language model to judge
[3767.26s -> 3773.50s]  which of the judgments is better, A or B. Now we have a particular algorithm then
[3773.50s -> 3779.10s]  for like basically taking all different judgments, calculating the meta judgments,
[3779.10s -> 3784.86s]  and then the ELO score amongst them. But the reason to do that is to create
[3784.86s -> 3791.26s]  preference pairs amongst judgments. So now we can say, okay, this judgment looks better than
[3791.26s -> 3799.10s]  that judgment because our meta judge, you know, tend to say that. And so we can construct
[3799.10s -> 3805.26s]  preference pairs, again with DPO, of which judgments are better. So now we've got two
[3805.26s -> 3810.62s]  types of preference pairs, the ones we had before, which were like response, you know,
[3810.62s -> 3817.74s]  response chosen is better than response rejected. But now we also have judgment chosen is better
[3817.74s -> 3823.98s]  than judgment rejected. And we train the model with both types of data. So this is different to
[3823.98s -> 3829.50s]  basically self-rewarding language models that I showed earlier only have the top part of this
[3830.14s -> 3835.50s]  picture, right? So it didn't really have an explicit mechanism to improve its ability to
[3836.46s -> 3846.86s]  evaluate things. And yeah, so this work, I think it's exciting because it helps. We actually get
[3846.86s -> 3861.18s]  better win rates on say our packet eval with that. And yeah, this plot, you can see again,
[3863.42s -> 3870.94s]  we see the improvement over iterations, but it's above the performance of the self-rewarding
[3870.94s -> 3878.30s]  model that doesn't have this meta judge training. And even the self-rewarding model
[3878.30s -> 3884.54s]  tends to plateau a bit here on iteration four, whereas it's still going up for the
[3884.54s -> 3891.18s]  meta-rewarding model. So I think that's pretty exciting. And yeah, I've got one more thing
[3891.18s -> 3903.58s]  to talk about, which is how to improve the chain of thoughts for judgments for evaluation.
[3903.58s -> 3910.38s]  So that's another recent work actually only out last week. So this is called,
[3911.18s -> 3920.86s]  this work's called Thinking LLM as a Judge. And the goal is to generate these long chain of
[3920.86s -> 3927.90s]  thoughts similar to O1, R1, but for the task of judgment of responses. Again, so that we have good
[3927.90s -> 3933.18s]  rewards for training our models. So here's an example from the model we trained of what it
[3933.18s -> 3940.46s]  can do. Outputs this evaluation plan of how it's going to evaluate and then sort of executes
[3940.46s -> 3947.10s]  on the plan and gives this final verdict. Yeah, so we have a sort of a training mechanism for that.
[3948.06s -> 3960.78s]  And the trick here is you can look at the evaluation task actually as a verifiable task
[3961.34s -> 3966.78s]  if you know which of two responses is better. So let's say you've got an instruction, you've
[3966.78s -> 3972.22s]  got response A and response B. If you know in advance that A is better or B is better,
[3973.18s -> 3980.14s]  then that's like a verifiable task, like the math tasks. We can compute the reward directly. We
[3980.14s -> 3990.70s]  don't need, say, a language model or LLM as a judge to agree with our output. So the trick
[3991.26s -> 3998.86s]  in this work, the first trick is to generate synthetic evaluation data so that we have
[3998.86s -> 4004.30s]  verifiable tasks so we know which one's better. And once we have that verifiable task, we can
[4004.30s -> 4010.94s]  essentially do something a bit like the iterative reasoning preference optimization IRPO, because
[4010.94s -> 4017.90s]  we can compute the rewards directly and build these preference pairs to improve the chain of
[4017.90s -> 4025.50s]  thoughts for evaluation. There's a couple of extra details here where in this particular case,
[4025.50s -> 4034.14s]  we actually asked it to do a plan first and then execute on the plan, which is the
[4034.14s -> 4044.94s]  left-hand part of this figure. So how do we create this verifiable data? So this comes from
[4044.94s -> 4052.38s]  a previous paper we did called self-taught evaluators. What we're going to do is we,
[4052.70s -> 4058.46s]  given a prompt x, we generate a good response with a language model, or at least we think is a
[4058.46s -> 4064.78s]  good response. Let's say it's a reasonable response. And then we generate a similar prompt,
[4064.78s -> 4072.86s]  x prime, which is similar but different to x. And then we also use the LLM, same LLM, to generate
[4072.86s -> 4081.10s]  a good response to x prime. We'll call that y prime. And now the hope is that, of course, because
[4081.82s -> 4092.70s]  x prime is different to x, y prime won't be as good a response to x. So that's the thing,
[4092.70s -> 4099.42s]  that basically y should be preferred over y prime for input x. So this now becomes our
[4099.42s -> 4106.46s]  verifiable task that we're going to use for training. So the only question there that was a bit
[4106.46s -> 4112.06s]  of an unknown was how do you make this similar but different prompt? And of course we use LLM
[4112.06s -> 4117.50s]  to do that as well. So we say please generate a modified instruction that's highly relevant but
[4117.50s -> 4121.90s]  not semantically identical to the instruction above. And then this is what gives us the
[4122.78s -> 4129.42s]  similar instruction which we can then generate the lower quality response for the original
[4129.42s -> 4137.02s]  instruction from. And yeah, that's roughly the higher level picture of this work.
[4137.98s -> 4146.78s]  And there's some ablation studies here where we showed that these plans are superior to not
[4147.34s -> 4153.74s]  thinking at all, so no chain of thought. But in general, it's good to have the plans
[4153.74s -> 4158.06s]  as unconstrained as possible. Like if you encourage them to be, for example, lists of
[4158.06s -> 4165.26s]  criteria or verification questions, which some other works have used with prompting,
[4165.26s -> 4172.54s]  then the results get worse. And I think that's kind of in line with the O1 R1 style results
[4172.54s -> 4177.58s]  as well, where basically you don't want to constrain too much the chain of thought thinking
[4177.58s -> 4183.82s]  processes of these language models, but you want to kind of train and find out what it's
[4184.62s -> 4194.54s]  going to be good at. And then, yeah, after we train this model using LAMA 3.1 or 3.3 70B as a
[4194.54s -> 4201.90s]  base, where it gets very good results, it's actually state of the art on this benchmark
[4201.90s -> 4207.90s]  called reward bench, which evaluates reward models for LLM as a judge, like generative
[4207.90s -> 4215.10s]  models. And it's also quite good on some harder evaluation tasks or some newer benchmarks that
[4215.10s -> 4226.78s]  just came out, like RM bench and Volo bench eval. And yeah, that's really all the things
[4226.78s -> 4231.26s]  I'm going to talk about. I think I talked about enough already, right? So just a little
[4231.26s -> 4238.22s]  bit of a summary of these recent works from the last year. Self-rewarding models,
[4240.22s -> 4244.86s]  they're models that can train themselves to get better. And the hope is that could be a path to
[4244.86s -> 4252.54s]  superhuman AI as the model improves itself. We've seen how verifiable rewards can help to
[4252.54s -> 4257.66s]  train chain of thought for better reasoning. So I showed you this iterative reasoning preference
[4257.66s -> 4265.74s]  optimization technique, but DeepSeek and O1 have related techniques, basically all using
[4265.74s -> 4270.30s]  these verifiable rewards on the output and then letting the chain of thought kind of
[4271.82s -> 4278.62s]  don't penalize it, just find ones that work well during your training cycle.
[4279.90s -> 4284.62s]  And then you can also use these verifiable rewards to improve the evaluation ability of
[4284.62s -> 4291.02s]  the model. So that's the thinking LLM as a judge that I just showed. And then of course,
[4291.02s -> 4295.98s]  if we have these better judges with these chain of thought, the whole thing can go in
[4295.98s -> 4302.94s]  a cycle, right? We can use those to help train to think on non-verifiable tasks because
[4302.94s -> 4309.34s]  we can use this thinking LLM as a judge to train those models. And we call that thinking
[4309.34s -> 4316.62s]  LLMs, which I showed earlier as well. And then finally, you can use this meta-rewarding
[4316.62s -> 4321.74s]  concept to judge their own judgments as another way of improving their evaluation ability.
[4322.54s -> 4329.18s]  So I've shown you a few sort of separate papers, but kind of the goal of the
[4329.90s -> 4335.10s]  bigger model release is to try and put some of these ideas together. So yeah, some of those
[4335.10s -> 4340.70s]  more recent things like meta-rewarding and thinking LLMs kind of need to go together with
[4340.70s -> 4348.70s]  the earlier ideas all in one system. And we'll see how far we can push that. And of course,
[4349.26s -> 4354.86s]  still looking for new ideas, right? And they're going to be coming in the coming days,
[4354.86s -> 4364.54s]  weeks, months, and years, I'm sure. So yeah, of course, there's lots of other directions.
[4365.34s -> 4373.58s]  And just to throw one out there is all the reasoning I've been talking about was with
[4374.22s -> 4379.18s]  chain of thoughts that were text, right? It's generating text from the language model.
[4379.18s -> 4385.74s]  Now, you don't have to do that, right? The transformer itself does reasoning by
[4387.58s -> 4394.70s]  all these multiplications inside the neural net. It's all manipulating vectors in the hidden
[4394.70s -> 4401.34s]  states of the network. And so why does this system two reasoning have to be tokens? Maybe
[4401.34s -> 4407.26s]  that could also be these continuous vectors as well. So we explored that in a recent paper,
[4407.82s -> 4415.98s]  a method called Coconut, where we replace the chain of thought of like outputting tokens with
[4415.98s -> 4423.50s]  outputting vectors instead. And we showed that has some promise actually. It could
[4425.02s -> 4432.46s]  at least match the performance on some tasks and even outperform classical chain of thought on some
[4432.46s -> 4439.82s]  more difficult search tasks. But these are all quite small scale tasks, so remains to be seen
[4439.82s -> 4446.06s]  sort of how far people can push that direction. I think there's some reasons to want to have
[4446.06s -> 4452.86s]  the chain of thought in human language, natural language. I think it's a nice thing for safety
[4453.82s -> 4463.34s]  and interpretability. But as I said, the neural network itself isn't interpretable in that way,
[4463.34s -> 4467.98s]  right? The internals of the transformer. So that's something we have to work out, I think.
[4470.78s -> 4476.06s]  And I got another slide about what else comes next. I think there's so much more exciting
[4476.14s -> 4485.82s]  research to be done. So Ilya Sitzkever in his Seek to Seek paper test of time award, that was this
[4485.82s -> 4494.30s]  last NeurIPS talk, he presented some things. This is a picture of what he was saying,
[4494.30s -> 4499.34s]  what comes next. He was mentioning agents, synthetic data, inference time compute,
[4500.22s -> 4505.58s]  reasoning, understanding, and being self-aware, which all makes sense. And I think these are
[4505.66s -> 4511.66s]  things that people are working on today. Well, maybe the self-aware ones is a little more
[4512.94s -> 4518.70s]  fuzzy, but the other ones at least. And yeah, I would say that I would just add some more
[4518.70s -> 4527.02s]  detail there. I think self-improving, self-evaluation is really important because
[4527.02s -> 4533.34s]  that bottlenecks performance. So using more of this inference time compute for evaluation is only
[4533.42s -> 4538.46s]  going to help self-improve the model. And I think that's sort of related to this self-aware
[4540.14s -> 4546.62s]  comment that he makes here, that a self-aware model might be more able to understand what
[4547.18s -> 4553.18s]  it knows and what it doesn't know, which is kind of evaluation. And then learning from
[4553.18s -> 4557.82s]  interaction, I think learning how to reason by actually interacting with people in the world,
[4557.82s -> 4564.14s]  internet or itself are important things. And that's related to the agent's point and
[4564.14s -> 4569.58s]  the synthetic data point he makes there. And then of course, it's not just about
[4569.58s -> 4574.38s]  improving the system two reasoning. I think if we can improve system one reasoning,
[4575.10s -> 4581.26s]  so like the transformer architecture itself, then that's great too. So maybe there's a better
[4581.26s -> 4590.86s]  attention model or maybe something new, a neural network layer we haven't come up with yet that
[4590.86s -> 4598.62s]  could change like the scaling laws and the performance of these models. And that's great too.
[4598.62s -> 4606.14s]  So yeah, plenty to do and it's going to be exciting to see what happens. Thank you.
