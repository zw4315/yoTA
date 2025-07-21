# Detected language: en (p=1.00)

[0.00s -> 10.00s]  Okay, so last lecture I gave an overview of language models
[10.00s -> 12.00s]  and what it means to build them from scratch
[12.00s -> 13.00s]  and why we want to do that.
[13.00s -> 15.00s]  I also talked about tokenization,
[15.00s -> 18.00s]  which is going to be the first half of the first assignment.
[18.00s -> 24.00s]  Today's lecture will be going through actually building a model.
[24.00s -> 29.00s]  We'll discuss the primitives in PyTorch that are needed.
[29.00s -> 33.00s]  We're going to start with tensors, build models, optimizers, and training loop,
[33.00s -> 37.00s]  and we're going to place close attention to efficiency,
[37.00s -> 43.00s]  in particular how we're using resources, both memory and compute.
[43.00s -> 49.00s]  Okay, so to motivate things a bit, here's some questions.
[49.00s -> 52.00s]  These questions are going to be answerable by napkin math,
[52.00s -> 55.00s]  so get your napkins out.
[55.00s -> 59.00s]  So how long would it take to train a 70 billion parameter dense transformer model
[59.00s -> 64.00s]  on 15 trillion tokens on 1,024 H100s?
[64.00s -> 68.00s]  Okay, so I'm just going to sketch out the,
[68.00s -> 71.00s]  give you a flavor of the type of things that we want to do.
[71.00s -> 74.00s]  Okay, so here's how you go about reasoning it.
[74.00s -> 82.00s]  You count the total number of flops needed to train,
[82.00s -> 87.00s]  so that's six times the number of parameters times the number of tokens.
[87.00s -> 89.00s]  Okay, and where does that come from?
[89.00s -> 92.00s]  That will be what we'll talk about in this lecture.
[92.00s -> 99.00s]  You can look at the promised number of flops per second that H100 gives you,
[99.00s -> 101.00s]  the MFU, which is something we'll see later.
[101.00s -> 104.00s]  Let's just set it to 0.5.
[104.00s -> 108.00s]  And you can look at the number of flops per day
[108.00s -> 112.00s]  that your hardware is going to give you at this particular MFU,
[112.00s -> 120.00s]  so 1,024 of them for one day.
[120.00s -> 123.00s]  And then you just divide the total number of flops you need
[123.00s -> 127.00s]  to train the model by the number of flops that you're supposed to get.
[127.00s -> 132.00s]  Okay, and that gives you about 144.
[132.00s -> 137.00s]  Okay, so this is very simple calculations at the end of the day.
[137.00s -> 142.00s]  We're going to go through a bit more where these numbers come from,
[142.00s -> 146.00s]  and in particular where the six times number of parameters
[146.00s -> 149.00s]  times number of tokens comes from.
[149.00s -> 151.00s]  Okay, so here's the question.
[151.00s -> 155.00s]  What is the largest model you can train on H8, H100, using Adam, W,
[155.00s -> 158.00s]  if you're not being too clever?
[158.00s -> 165.00s]  Okay, so H100 has 80 gigabytes of HBM memory.
[165.00s -> 169.00s]  The number of bytes per parameter that you need for the parameters,
[169.00s -> 173.00s]  the gradient optimizer state is 16,
[173.00s -> 176.00s]  and we'll talk more about where that comes from.
[176.00s -> 180.00s]  And the number of parameters is basically the total amount of memory
[180.00s -> 183.00s]  divided by the number of bytes you need per parameter,
[183.00s -> 189.00s]  and that gives you about 40 billion parameters.
[189.00s -> 194.00s]  Okay, and this is very rough because it doesn't take you into activation,
[194.00s -> 197.00s]  which depends on batch size and sequence length,
[197.00s -> 199.00s]  which I'm not really going to talk about,
[199.00s -> 202.00s]  but will be important for assignment one.
[202.00s -> 205.00s]  Okay, so this is a rough back of the calculation,
[205.00s -> 208.00s]  and this is something that you're probably not used to doing.
[208.00s -> 210.00s]  You just implement the model, you train it,
[210.00s -> 211.00s]  and what happens, happens,
[211.00s -> 214.00s]  but remember that efficiency is the name of the game,
[214.00s -> 215.00s]  and to be efficient,
[215.00s -> 218.00s]  you have to know exactly how many flops you're actually expending,
[218.00s -> 220.00s]  because when these numbers get large,
[220.00s -> 222.00s]  these directly translate into dollars,
[222.00s -> 226.00s]  and you want that to be as small as possible.
[226.00s -> 229.00s]  Okay, so we'll talk more about the details
[229.00s -> 234.00s]  of how these numbers arise.
[234.00s -> 237.00s]  You know, we will not actually go over the transformer,
[237.00s -> 244.00s]  so Tatsu's going to talk over the conceptual overview of that next time,
[244.00s -> 247.00s]  and there's many ways you can learn about a transformer
[247.00s -> 249.00s]  if you haven't already looked at it.
[249.00s -> 250.00s]  There's assignment one.
[250.00s -> 251.00s]  If you do assignment one,
[251.00s -> 253.00s]  you'll definitely know what a transformer is,
[253.00s -> 255.00s]  and the handout actually does a pretty good job
[255.00s -> 257.00s]  of walking through all the different pieces.
[257.00s -> 258.00s]  There's a mathematical description.
[258.00s -> 260.00s]  If you like pictures, there's pictures.
[260.00s -> 264.00s]  There's a lot of stuff you can look on online.
[264.00s -> 267.00s]  But instead, I'm going to work with simpler models
[267.00s -> 269.00s]  and really talk about the primitives
[269.00s -> 271.00s]  and the resource accounting piece.
[271.00s -> 273.00s]  Okay, so remember last time I said
[273.00s -> 275.00s]  what kinds of knowledge can you learn?
[275.00s -> 278.00s]  So mechanics, in this lecture,
[278.00s -> 280.00s]  it's going to be just PyTorch
[280.00s -> 282.00s]  and understanding how PyTorch works
[282.00s -> 285.00s]  at a fairly primitive level.
[285.00s -> 287.00s]  So that will be pretty straightforward.
[287.00s -> 290.00s]  Mindset is about resource accounting,
[290.00s -> 291.00s]  and it's not hard.
[291.00s -> 293.00s]  You just have to do it.
[293.00s -> 296.00s]  And intuitions, unfortunately,
[296.00s -> 298.00s]  this is just going to be broad strokes for now.
[298.00s -> 300.00s]  Actually, there's not really much intuition
[300.00s -> 301.00s]  that I'm going to talk about
[301.00s -> 304.00s]  in terms of how anything we're doing
[304.00s -> 305.00s]  translates to good models.
[305.00s -> 310.00s]  This is more about the mechanics and mindset.
[310.00s -> 315.00s]  Okay, so let's start with memory accounting.
[315.00s -> 317.00s]  And then I'll talk about compute accounting,
[317.00s -> 320.00s]  and then we'll build up, bottom up.
[320.00s -> 324.00s]  Okay, so the best place to start is a tensor.
[324.00s -> 326.00s]  So tensors are the building block
[326.00s -> 328.00s]  for storing everything in deep learning.
[328.00s -> 332.00s]  Parameters, gradients, optimizers, data, activations,
[332.00s -> 334.00s]  and there's sort of these atoms.
[334.00s -> 338.00s]  You can read lots of documentation about them.
[338.00s -> 341.00s]  You're probably very familiar with how to create tensors.
[341.00s -> 344.00s]  There's creating tensors different ways.
[344.00s -> 347.00s]  You can also create a tensor and not initialize it
[347.00s -> 351.00s]  and use some special initialization
[351.00s -> 356.00s]  for the parameters, if you want.
[356.00s -> 361.00s]  Okay, so those are tensors.
[361.00s -> 363.00s]  So let's talk about memory
[363.00s -> 366.00s]  and how much memory tensors take up.
[366.00s -> 370.00s]  So every tensor that we'll probably be interested in
[370.00s -> 372.00s]  is stored as a floating point number.
[372.00s -> 375.00s]  And so there's many ways to represent floating point.
[375.00s -> 380.00s]  So the most default way is float 32.
[380.00s -> 384.00s]  And float 32 has 32 bits.
[384.00s -> 387.00s]  They're allocated one for sine, eight for exponent,
[387.00s -> 390.00s]  and 23 for the fraction.
[390.00s -> 392.00s]  So exponent gives you dynamic range
[392.00s -> 395.00s]  and fraction gives you different,
[395.00s -> 397.00s]  basically specifies different values.
[397.00s -> 401.00s]  So float 32 is also known as FP32,
[401.00s -> 404.00s]  or single precision,
[404.00s -> 409.00s]  is sort of the gold standard in computing.
[409.00s -> 412.00s]  Some people also refer to float 32 as full precision.
[412.00s -> 414.00s]  That's a little bit confusing
[414.00s -> 417.00s]  because full is really depending on who you're talking to.
[417.00s -> 419.00s]  If you're talking to a scientific computing person,
[419.00s -> 424.00s]  they'll kind of laugh at you when you say float 32 is really full
[424.00s -> 427.00s]  because they'll use float 64 or even more.
[427.00s -> 429.00s]  But if you're talking to a machine learning person,
[429.00s -> 432.00s]  float 32 is the max you'll ever probably need to go
[432.00s -> 437.00s]  because deep learning is kind of sloppy like that.
[437.00s -> 440.00s]  Okay, so let's look at the memory.
[440.00s -> 442.00s]  So the memory is very simple.
[442.00s -> 444.00s]  It's determined by the number of values you have in your tensor
[444.00s -> 446.00s]  and the data type of each value.
[446.00s -> 450.00s]  Okay, so if you create a torch tensor of a four by eight matrix,
[450.00s -> 455.00s]  the default will give you a type of float 32.
[455.00s -> 459.00s]  The size is four by eight,
[459.00s -> 462.00s]  and the number of elements is 32.
[462.00s -> 465.00s]  Each element size is four bytes.
[465.00s -> 467.00s]  32 bits is four bytes.
[467.00s -> 471.00s]  And the memory usage is simply the number of elements
[471.00s -> 475.00s]  times the number of, size of each element,
[475.00s -> 477.00s]  and that will give you 128 bytes.
[477.00s -> 480.00s]  Okay, so this should be pretty easy.
[480.00s -> 482.00s]  And just to give some intuition,
[482.00s -> 486.00s]  if you get one matrix in the P4 layer of GPT-3
[486.00s -> 488.00s]  is this number by this number,
[488.00s -> 491.00s]  and that gives you 2.3 gigabytes.
[491.00s -> 494.00s]  Okay, so that's one matrix.
[494.00s -> 498.00s]  These matrices can be pretty big.
[498.00s -> 502.00s]  Okay, so float 32 is a default.
[502.00s -> 505.00s]  But of course, these matrices get big,
[505.00s -> 509.00s]  so naturally you want to make them smaller,
[509.00s -> 510.00s]  so you use less memory.
[510.00s -> 512.00s]  And also it turns out if you make them smaller,
[512.00s -> 515.00s]  you also make it go faster, too.
[515.00s -> 522.00s]  Okay, so another representation is called float 16,
[522.00s -> 527.00s]  and as the name suggests, it's 16 bits
[527.00s -> 531.00s]  where both the exponent and the fraction are shrunk down
[531.00s -> 536.00s]  from eight to five and 23 to 10.
[536.00s -> 539.00s]  Okay, so this is known as half precision,
[539.00s -> 542.00s]  and it cuts down half the memory.
[542.00s -> 545.00s]  And that's all great,
[545.00s -> 551.00s]  except for the dynamic range for these float 16 isn't great.
[551.00s -> 554.00s]  So for example, if you try to make a number
[554.00s -> 561.00s]  like one e minus eight in float 16,
[561.00s -> 564.00s]  it basically rounds out to zero,
[564.00s -> 566.00s]  and you get underflow.
[566.00s -> 568.00s]  Okay, so the float 16 is not great
[568.00s -> 571.00s]  for representing very small numbers
[571.00s -> 574.00s]  or very big numbers, as a matter of fact.
[574.00s -> 578.00s]  So if you use float 16 for training,
[578.00s -> 581.00s]  for small models it's probably going to be okay,
[581.00s -> 585.00s]  but for large models when you're having lots of matrices
[585.00s -> 588.00s]  and you can get instability or underflow or overflow
[588.00s -> 591.00s]  and bad things happen.
[591.00s -> 596.00s]  Okay, so one thing that has happened,
[596.00s -> 599.00s]  which is nice, is there's been another representation
[599.00s -> 603.00s]  of b float 16, which stands for brain float.
[603.00s -> 606.00s]  This was developed in 2018 to address the issue
[606.00s -> 609.00s]  that for deep learning,
[609.00s -> 611.00s]  we actually care about dynamic range
[611.00s -> 615.00s]  more than we care about this fraction.
[615.00s -> 618.00s]  So basically b of 16 allocates more to the exponent
[618.00s -> 620.00s]  and less to the fraction.
[620.00s -> 624.00s]  Okay, so it uses the same memory as float 16,
[624.00s -> 628.00s]  but it has a dynamic range of float 32.
[628.00s -> 630.00s]  Okay, so that sounds really good,
[630.00s -> 634.00s]  and it actually catches at this resolution,
[634.00s -> 636.00s]  which is determined by this fraction is worse,
[636.00s -> 639.00s]  but this doesn't matter as much for deep learning.
[639.00s -> 642.00s]  So now if you try to create a tensor
[642.00s -> 646.00s]  with one e minus eight in b of 16,
[646.00s -> 649.00s]  then you get something that's not zero.
[651.00s -> 654.00s]  Okay, so you can dive into the details.
[654.00s -> 655.00s]  I'm not going to go into this,
[655.00s -> 658.00s]  but you can stare at the actual full specs
[658.00s -> 661.00s]  of all the different floating point operations.
[662.00s -> 664.00s]  Okay, so b of 16 is basically
[664.00s -> 668.00s]  what you will typically use to do computations
[668.00s -> 671.00s]  because it's sort of good enough
[671.00s -> 673.00s]  for a free-for-all computation.
[673.00s -> 677.00s]  It turns out that for storing optimizer states
[677.00s -> 680.00s]  and parameters, you still need float 32
[680.00s -> 684.00s]  for otherwise your training will go haywire.
[686.00s -> 688.00s]  So if you're bold,
[688.00s -> 693.00s]  so now we have something called FP8, or 8-bit,
[693.00s -> 695.00s]  and as the name suggests,
[695.00s -> 700.00s]  this was developed in 2022 by NVIDIA,
[700.00s -> 704.00s]  so now they have, essentially,
[704.00s -> 708.00s]  if you look at FP and b of 16, it's like this,
[708.00s -> 710.00s]  and FP, wow, you really don't have
[710.00s -> 712.00s]  that many bits to store stuff.
[712.00s -> 714.00s]  Right, so it's very crude.
[714.00s -> 717.00s]  There's two sort of variants depending on
[717.00s -> 721.00s]  if you want to have more resolution or more dynamic range.
[723.00s -> 725.00s]  And I'm not going to say too much about this,
[725.00s -> 728.00s]  but FP8 is supported by H100.
[728.00s -> 731.00s]  It's not really available on a previous generation.
[733.00s -> 736.00s]  But at a high level, training with float 32,
[736.00s -> 741.00s]  which I think is what you would do
[741.00s -> 743.00s]  if you're not trying to optimize too much,
[743.00s -> 745.00s]  and it's sort of safe.
[745.00s -> 747.00s]  It requires more memory.
[747.00s -> 752.00s]  You can go down to FP8 or BF16,
[754.00s -> 756.00s]  but you can get some instability.
[756.00s -> 758.00s]  Basically, I don't think you would probably want to use
[758.00s -> 762.00s]  a float 16 at this point for deep learning.
[765.00s -> 769.00s]  And you can become more sophisticated
[769.00s -> 773.00s]  by looking at particular places in your pipeline,
[774.00s -> 776.00s]  either forward pass or backward pass
[776.00s -> 779.00s]  or optimizers or gradient accumulation,
[779.00s -> 782.00s]  and really figure out what the minimum precision you need
[782.00s -> 784.00s]  at this particular places,
[784.00s -> 787.00s]  and that's called, gets into mixed precision training.
[787.00s -> 791.00s]  So for example, some people like to use float 32
[791.00s -> 794.00s]  for the attention to make sure
[794.00s -> 797.00s]  that doesn't kind of get messed up,
[797.00s -> 799.00s]  but for simple feed forward passes
[799.00s -> 802.00s]  with MatMals, BF16 is fine.
[804.00s -> 805.00s]  Okay.
[805.00s -> 808.00s]  Pause a bit for questions.
[808.00s -> 810.00s]  So we talked about tensors,
[810.00s -> 814.00s]  and we looked at, depending on what representation,
[814.00s -> 817.00s]  how much storage they take.
[817.00s -> 818.00s]  Yeah.
[818.00s -> 820.00s]  Can you just clarify about the mixed position,
[820.00s -> 822.00s]  like when you would use 32 and the B float?
[822.00s -> 824.00s]  Yeah, so the question is,
[824.00s -> 829.00s]  when would you use float 32 or BF16?
[830.00s -> 833.00s]  I don't have time to get into the exact details,
[833.00s -> 834.00s]  and it sort of varies
[834.00s -> 836.00s]  depending on the model size and everything,
[836.00s -> 840.00s]  but generally for the parameters and optimizers states,
[840.00s -> 842.00s]  you use float 32.
[842.00s -> 843.00s]  You can think about BF16
[843.00s -> 846.00s]  as something that's more transitory.
[846.00s -> 848.00s]  You basically take your parameters,
[848.00s -> 850.00s]  you cast it to BF16,
[850.00s -> 852.00s]  and you kind of run ahead with that model,
[852.00s -> 855.00s]  but then the thing that you're gonna accumulate over time,
[855.00s -> 858.00s]  you want to have higher precision.
[858.00s -> 859.00s]  Yeah.
[861.00s -> 862.00s]  Okay.
[862.00s -> 865.00s]  So, now let's talk about compute.
[865.00s -> 868.00s]  So that was memory.
[868.00s -> 869.00s]  So,
[871.00s -> 875.00s]  compute obviously depends on what the hardware is.
[875.00s -> 877.00s]  By default, tensors are stored in CPU.
[877.00s -> 879.00s]  So for example, if you just, in PyTorch,
[879.00s -> 882.00s]  say x equals torch at zero is 3232,
[882.00s -> 884.00s]  then it'll put it on your CPU.
[884.00s -> 887.00s]  It'll be in the CPU memory.
[888.00s -> 890.00s]  Of course, that's no good,
[890.00s -> 892.00s]  because if you're not using your GPU,
[892.00s -> 894.00s]  then you're gonna be orders of magnitude too slow,
[894.00s -> 897.00s]  so you need to explicitly say in PyTorch
[897.00s -> 900.00s]  that you need to move it to the GPU,
[900.00s -> 901.00s]  and this is,
[902.00s -> 906.00s]  it's actually, just to make it very clear in pictures,
[906.00s -> 908.00s]  there's a CPU, it has RAM,
[908.00s -> 912.00s]  and that has to be moved over to the GPU.
[912.00s -> 914.00s]  There's a data transfer,
[914.00s -> 917.00s]  which is cut, which takes some work.
[919.00s -> 920.00s]  Takes some time.
[920.00s -> 921.00s]  Okay?
[921.00s -> 924.00s]  So, whenever you have a tensor in PyTorch,
[924.00s -> 926.00s]  you should always keep in your mind
[926.00s -> 927.00s]  where is this residing,
[927.00s -> 929.00s]  because just looking at the variable
[929.00s -> 930.00s]  or just looking at the code,
[930.00s -> 931.00s]  you can't always tell.
[931.00s -> 933.00s]  And if you want to be careful about
[933.00s -> 936.00s]  computation and data movement,
[936.00s -> 939.00s]  you have to really know where it is.
[939.00s -> 942.00s]  You can probably do things like assert
[942.00s -> 944.00s]  where it is in various places of code,
[944.00s -> 947.00s]  just to document or be sure.
[948.00s -> 949.00s]  Okay, so,
[952.00s -> 955.00s]  so let's look at what hardware we have.
[955.00s -> 959.00s]  So, we have, in this case, we have one GPU.
[959.00s -> 962.00s]  This was run on the H100 clusters
[962.00s -> 964.00s]  that you guys have access to,
[964.00s -> 966.00s]  and this GPU is H100,
[967.00s -> 971.00s]  GPU is H100, 80 gigabytes of high bandwidth memory,
[975.00s -> 979.00s]  and it gives you the cache size and so on.
[979.00s -> 980.00s]  Okay, so,
[983.00s -> 987.00s]  if you have, remember the X is on CPU,
[987.00s -> 991.00s]  you can move it just by specifying two,
[991.00s -> 994.00s]  which is kind of a general PyTorch function.
[994.00s -> 996.00s]  You can also create a tensor directly on a GPU,
[996.00s -> 999.00s]  so you don't have to move it at all.
[999.00s -> 1002.00s]  And if everything goes well,
[1002.00s -> 1006.00s]  I'm looking at the memory allocated before and after,
[1006.00s -> 1009.00s]  the difference should be exactly
[1010.00s -> 1014.00s]  two 32 by 32 matrices of four byte floats.
[1017.00s -> 1019.00s]  Okay, so it's A192.
[1021.00s -> 1023.00s]  Okay, so this is just a sanity check
[1023.00s -> 1026.50s]  that the code is doing what is advertised.
[1030.00s -> 1034.00s]  Okay, so now you have your tensors on the GPU.
[1034.00s -> 1036.00s]  What do you do?
[1036.00s -> 1038.00s]  So, there's many operations
[1038.00s -> 1040.00s]  that you'll be needing for assignment one,
[1040.00s -> 1044.00s]  and in general, to do any deep learning application.
[1044.00s -> 1045.00s]  And most tensors,
[1045.00s -> 1048.00s]  you just create by performing operations on other tensors,
[1048.00s -> 1052.00s]  and each operation has some memory and compute footprints,
[1052.00s -> 1056.00s]  so let's make sure we understand that.
[1056.00s -> 1061.00s]  So first of all, what is actually a tensor in PyTorch?
[1061.00s -> 1064.00s]  Tensors are like a mathematical object.
[1064.00s -> 1067.00s]  In PyTorch, they're actually pointers
[1067.00s -> 1070.00s]  into some allocated memory.
[1070.00s -> 1073.00s]  Okay, so if you have, let's say,
[1074.00s -> 1077.00s]  a matrix, four by four matrix,
[1077.00s -> 1081.00s]  what it actually looks like is a long array.
[1081.00s -> 1084.00s]  And what the tensor has is metadata
[1084.00s -> 1088.00s]  that specifies how to get to address into that array.
[1088.00s -> 1091.00s]  And the metadata is going to be two numbers,
[1091.00s -> 1094.00s]  a stride for each, or actually,
[1094.00s -> 1098.00s]  one number per dimension of the tensor.
[1098.00s -> 1101.00s]  In this case, because there's two dimensions,
[1101.00s -> 1104.00s]  it's stride zero and stride one.
[1106.00s -> 1109.00s]  Stride zero specifies
[1109.00s -> 1112.00s]  if you were in dimension zero,
[1112.00s -> 1116.00s]  to get to the next row, to increment that index,
[1116.00s -> 1118.00s]  how many do you have to skip?
[1118.00s -> 1121.00s]  And so going down the rows, you skip four,
[1121.00s -> 1124.00s]  so stride zero is four.
[1124.00s -> 1129.00s]  And to go to the next column, you skip one.
[1129.00s -> 1133.00s]  So stride one is one, okay?
[1133.00s -> 1135.00s]  So with that, you find an element,
[1135.00s -> 1138.00s]  let's say one, two, one comma two,
[1139.00s -> 1143.00s]  it simply just multiply the indexes by the stride,
[1143.00s -> 1147.00s]  and you get to your index, which is six here.
[1148.00s -> 1151.00s]  So that would be here or here.
[1151.00s -> 1153.00s]  Okay, so that's basically what's going on
[1153.00s -> 1156.00s]  underneath the hood for tensors.
[1157.00s -> 1160.00s]  Okay, so this is relevant because
[1163.00s -> 1166.00s]  you can have multiple tensors that use the same storage.
[1166.00s -> 1168.00s]  And this is useful because you don't want to copy
[1168.00s -> 1170.00s]  the tensor all over the place.
[1170.00s -> 1174.00s]  So imagine you have a two by three matrix here.
[1174.00s -> 1178.00s]  Many operations don't actually create a new tensor,
[1178.00s -> 1180.00s]  they just create a different view.
[1180.00s -> 1181.00s]  And it doesn't make a copy,
[1181.00s -> 1184.00s]  so you have to make sure that
[1185.00s -> 1188.00s]  your mutations, if you start mutating one tensor,
[1188.00s -> 1191.00s]  it's gonna cause the other one to mutate.
[1191.00s -> 1195.00s]  Okay, so for example, if you just get
[1196.00s -> 1200.00s]  row zero, okay, so remember y is this tensor,
[1202.00s -> 1205.00s]  sorry, x is one, two, three, four, five, six,
[1205.00s -> 1209.00s]  and y is x zero, which is just the first row.
[1210.00s -> 1212.00s]  And you can sort of double check,
[1212.00s -> 1214.00s]  there's this function in row that says
[1214.00s -> 1217.00s]  if you look at the underlying storage,
[1217.00s -> 1220.00s]  whether these two tensors have the same storage or not.
[1220.00s -> 1223.00s]  So this definitely doesn't copy the tensor,
[1223.00s -> 1225.00s]  it just creates a view.
[1226.00s -> 1228.00s]  You can get column one.
[1229.00s -> 1232.00s]  This also doesn't copy the tensor.
[1233.00s -> 1235.00s]  Oops, don't need to do that.
[1235.00s -> 1237.00s]  You can call a view function,
[1237.00s -> 1240.00s]  which can take any tensor and
[1240.00s -> 1244.00s]  look at it in terms of different dimensions.
[1244.00s -> 1248.00s]  Two by three, actually this should be
[1248.00s -> 1252.00s]  maybe the other way around, as a three by two tensor.
[1253.00s -> 1258.00s]  So that also doesn't change doing copying.
[1258.00s -> 1260.00s]  You can transpose.
[1261.00s -> 1263.00s]  That also doesn't copy.
[1263.00s -> 1267.00s]  And then, like I said, if you start mutating x,
[1268.00s -> 1271.00s]  then y actually gets mutated as well,
[1271.00s -> 1273.00s]  because x and y are just pointers
[1273.00s -> 1275.00s]  into the same underlying storage.
[1275.00s -> 1277.00s]  Okay, so things are,
[1278.00s -> 1281.00s]  one thing that you have to be careful of
[1281.00s -> 1284.00s]  is that some views are contiguous,
[1284.00s -> 1286.00s]  which means that if you run through the tensor,
[1286.00s -> 1291.00s]  it's like just going through this array in your storage.
[1292.00s -> 1294.00s]  But some are not.
[1294.00s -> 1296.00s]  So in particular, if you transpose it,
[1296.00s -> 1300.00s]  now what does it mean when you're transposing it?
[1300.00s -> 1302.00s]  You're sort of going down now.
[1302.00s -> 1305.00s]  So if you imagine going through the tensor,
[1305.00s -> 1307.00s]  you're kind of skipping around.
[1307.00s -> 1310.00s]  And if you have a non-contiguous tensor,
[1310.00s -> 1314.00s]  then if you try to further view it in a different way,
[1314.00s -> 1317.00s]  then this is not gonna work.
[1317.00s -> 1318.00s]  Okay?
[1318.00s -> 1321.00s]  So in some cases, if you have a non-contiguous tensor,
[1321.00s -> 1323.00s]  you can make it contiguous first,
[1323.00s -> 1326.00s]  and then you can apply whatever viewing operation
[1326.00s -> 1328.00s]  you want to it.
[1328.00s -> 1331.00s]  And then in this case, x and y
[1332.00s -> 1334.00s]  do not have the same storage,
[1334.00s -> 1338.00s]  because contiguous, in this case, makes a copy.
[1340.00s -> 1345.00s]  Okay, so this is just ways of slicing and dicing a tensor.
[1347.00s -> 1350.00s]  Views are free, so feel free to use them,
[1350.00s -> 1354.00s]  define different variables to make it sort of easier
[1354.00s -> 1356.00s]  to read your code,
[1356.00s -> 1359.00s]  because they're not allocating any memory.
[1359.00s -> 1363.00s]  But remember that contiguous or reshape,
[1363.00s -> 1366.00s]  which is basically contiguous.view,
[1366.00s -> 1368.00s]  can create a copy,
[1368.00s -> 1372.00s]  and so just be careful what you're doing.
[1372.00s -> 1375.00s]  Okay, questions before moving on?
[1379.00s -> 1380.00s]  All right.
[1380.00s -> 1384.00s]  So hopefully a lot of this will be reviewed
[1384.00s -> 1387.00s]  for those of you who have done a lot of PyTorch before,
[1387.00s -> 1390.00s]  but it's helpful to just do it systematically
[1390.00s -> 1392.00s]  and make sure we're on the same page.
[1392.00s -> 1397.00s]  So here's some operations that do create new tensors.
[1398.00s -> 1401.00s]  And in particular, element-wise operations
[1401.00s -> 1403.00s]  all create new tensors, obviously,
[1403.00s -> 1407.00s]  because you need somewhere else to store the new value.
[1407.00s -> 1410.00s]  There's a, you know, triangular U
[1410.00s -> 1413.00s]  is also an element operation that comes in handy
[1413.00s -> 1416.00s]  when you want to create a causal attention mask,
[1416.00s -> 1420.00s]  which you'll need for your assignment.
[1420.00s -> 1424.00s]  But nothing is interesting, that interesting here.
[1424.00s -> 1429.00s]  Okay, so let's talk about matmals.
[1429.00s -> 1431.00s]  So the bread and butter of deep learning
[1431.00s -> 1433.00s]  is matrix multiplications.
[1433.00s -> 1436.00s]  And I'm sure all of you have done a matrix multiplication,
[1436.00s -> 1438.00s]  but just in case, this is what it looks like.
[1438.00s -> 1441.00s]  You take a 16 by 32 times a 32 by two matrix,
[1441.00s -> 1444.00s]  you get a 16 by two matrix.
[1444.00s -> 1446.00s]  And, but in general,
[1448.00s -> 1452.00s]  when we do our machine learning application,
[1453.00s -> 1457.00s]  all operations are, you want to do in a batch.
[1457.00s -> 1458.00s]  And in the case of language models,
[1458.00s -> 1461.00s]  this usually means for every example in a batch
[1461.00s -> 1463.00s]  and for every sequence in a batch,
[1463.00s -> 1465.00s]  you want to do something.
[1465.00s -> 1467.00s]  Okay, so generally what you're gonna have
[1467.00s -> 1470.00s]  instead of just a matrix is you're gonna have a tensor
[1470.00s -> 1473.00s]  where the dimensions are typically batch, sequence,
[1473.00s -> 1476.00s]  and then whatever thing you're trying to do.
[1476.00s -> 1479.00s]  In this case, it's a matrix for every token
[1479.00s -> 1481.00s]  in your data set.
[1482.00s -> 1485.00s]  And so, you know, PyTorch is nice enough
[1485.00s -> 1487.00s]  to make this work well for you,
[1487.00s -> 1491.00s]  so when you take this four dimensional tensor
[1493.00s -> 1497.00s]  and this matrix, what actually ends up happening
[1497.00s -> 1501.00s]  is that for every batch, every example, and every token,
[1501.00s -> 1505.00s]  you're multiplying these two matrices, okay?
[1505.00s -> 1507.00s]  And then the result is that you get
[1507.00s -> 1512.00s]  your resulting matrix for each of the first two elements.
[1512.00s -> 1514.00s]  So this is just, there's nothing fancy going on,
[1514.00s -> 1516.00s]  but this is just a pattern
[1516.00s -> 1520.00s]  that I think is helpful to think about.
[1524.00s -> 1528.00s]  Okay, so I'm gonna take a little bit of a digression
[1528.00s -> 1530.00s]  and talk about INOPs.
[1531.00s -> 1535.00s]  And so the motivation for INOPs is the following.
[1535.00s -> 1541.00s]  So normally, in PyTorch, you define some tensors,
[1541.00s -> 1543.00s]  and then you see stuff like this,
[1543.00s -> 1547.00s]  where you take x and multiply by y transpose minus two minus one.
[1547.00s -> 1550.00s]  And you kind of look at this and you say,
[1550.00s -> 1552.00s]  okay, what is minus two?
[1552.00s -> 1555.00s]  Well, I think that's the sequence,
[1555.00s -> 1557.00s]  and then minus one is this hidden
[1557.00s -> 1559.00s]  because you're indexing backwards.
[1559.00s -> 1561.00s]  And it's really easy to mess this up
[1561.00s -> 1563.00s]  because if you look at it in your code
[1563.00s -> 1565.00s]  you see minus one, minus two.
[1565.00s -> 1567.00s]  You're kind of, if you're good,
[1567.00s -> 1569.00s]  you write a bunch of comments,
[1569.00s -> 1572.00s]  but then the comments can get out of date with the code
[1572.00s -> 1576.00s]  and then you have a bad time debugging.
[1576.00s -> 1580.00s]  So the solution is to use INOPs here.
[1580.00s -> 1584.00s]  So this is inspired by Einstein's summation notation.
[1584.00s -> 1586.00s]  And the idea is that we're just gonna name
[1586.00s -> 1591.00s]  all the dimensions instead of, you know,
[1591.00s -> 1594.00s]  relying on indices, essentially.
[1594.00s -> 1596.00s]  Okay, so there's a library called JAX typing
[1596.00s -> 1602.00s]  which is helpful for, as a way
[1602.00s -> 1606.00s]  to specify the dimensions in the types.
[1606.00s -> 1610.00s]  So normally, in PyTorch, you would just define,
[1610.00s -> 1612.00s]  write your code, and then you would comment,
[1612.00s -> 1614.00s]  oh, here's what the dimensions would be.
[1614.00s -> 1618.00s]  So if you use JAX typing, then you have this notation
[1618.00s -> 1620.00s]  where, as a string, you just write down
[1620.00s -> 1622.00s]  what the dimensions are.
[1622.00s -> 1625.00s]  So this is a slightly kind of more natural way
[1625.00s -> 1627.00s]  of documenting.
[1627.00s -> 1630.00s]  Now, notice that there's no enforcement here, right,
[1630.00s -> 1632.00s]  because PyTorch types are sort of
[1632.00s -> 1636.00s]  a little bit of a lie in PyTorch, so.
[1636.00s -> 1637.00s]  It can be enforced.
[1637.00s -> 1639.00s]  You can use a checker, right?
[1639.00s -> 1640.00s]  Yeah.
[1640.00s -> 1643.00s]  There is a check, but not by default.
[1647.00s -> 1651.00s]  Okay, so let's look at the, you know, Einstein.
[1651.00s -> 1655.00s]  So Einstein is basically matrix multiplication on steroids
[1655.00s -> 1657.00s]  with good bookkeeping.
[1657.00s -> 1660.00s]  So here's our example here.
[1660.00s -> 1663.00s]  We have X, which is, let's just think about this as,
[1663.00s -> 1665.00s]  you have a batch dimension, you have a sequence dimension,
[1665.00s -> 1670.00s]  and then you have four hiddens, and Y is the same size.
[1671.00s -> 1674.00s]  You originally had to do this thing,
[1674.00s -> 1677.00s]  and now what you do instead is
[1677.00s -> 1682.00s]  you basically write down the dimensions,
[1682.00s -> 1685.00s]  names of the dimensions of the two tensors,
[1685.00s -> 1688.00s]  so batch sequence one hidden, batch sequence two hidden,
[1688.00s -> 1691.00s]  and you just write what you,
[1691.00s -> 1694.00s]  dimensions should appear in the output.
[1694.00s -> 1696.00s]  Okay, so I write batch here,
[1696.00s -> 1700.00s]  because I just want to basically, you know,
[1700.00s -> 1704.00s]  carry that over, and then I write seek one and seek two.
[1704.00s -> 1707.00s]  And notice that I don't write hidden,
[1707.00s -> 1709.00s]  and any dimension that is not named in output
[1709.00s -> 1713.00s]  is just summed over, and any dimension that is named
[1713.00s -> 1716.00s]  is sort of just iterated over.
[1716.00s -> 1717.00s]  Okay?
[1717.00s -> 1720.00s]  So, once you get used to this,
[1720.00s -> 1723.00s]  this is actually very, very, you know, helpful
[1723.00s -> 1725.00s]  and maybe looks, if you've seen this for the first time,
[1725.00s -> 1727.00s]  it might seem a bit, you know, strange and long,
[1727.00s -> 1729.00s]  but trust me, once you get used to it,
[1729.00s -> 1733.00s]  it'll be better than doing minus two, minus one.
[1733.00s -> 1736.00s]  If you're a little bit, you know, slicker,
[1736.00s -> 1739.00s]  you can use dot dot dot to represent
[1739.00s -> 1741.00s]  broadcasting over any number of dimensions,
[1741.00s -> 1746.00s]  so in this case, instead of writing batch,
[1746.00s -> 1747.00s]  I can just write dot dot dot,
[1747.00s -> 1749.00s]  and this would handle the case where
[1749.00s -> 1752.00s]  instead of maybe batch, I have batch one, batch two,
[1752.00s -> 1757.00s]  or some other arbitrary long sequence.
[1757.00s -> 1758.00s]  Yeah, question?
[1758.00s -> 1760.00s]  Does force compile this,
[1760.00s -> 1764.00s]  like, is it guaranteed to compile to a position?
[1764.00s -> 1766.00s]  I guess.
[1766.00s -> 1767.00s]  So the question is,
[1767.00s -> 1770.00s]  is it guaranteed to compile to something efficient?
[1770.00s -> 1775.00s]  This, I think the short answer is yes.
[1775.00s -> 1777.00s]  I don't know if you have any, you know, nuances.
[1777.00s -> 1779.00s]  We'll figure out the best way to reduce,
[1779.00s -> 1781.00s]  the best order of dimensions to reduce,
[1781.00s -> 1783.00s]  and then use that.
[1783.00s -> 1784.00s]  If you use it within force compile,
[1784.00s -> 1785.00s]  only do that one time,
[1785.00s -> 1787.00s]  and then reuse the same implementation
[1787.00s -> 1788.00s]  over and over again.
[1788.00s -> 1791.00s]  It'll be better than anything designed like that.
[1791.00s -> 1794.00s]  Yeah.
[1794.00s -> 1796.00s]  Okay.
[1796.00s -> 1800.00s]  So let's look at reduce.
[1800.00s -> 1802.00s]  So reduce operates on one tensor,
[1802.00s -> 1805.00s]  and it basically aggregates some dimension
[1805.00s -> 1807.00s]  or dimensions of the tensor.
[1807.00s -> 1810.00s]  So you have this tensor before you would write mean
[1810.00s -> 1814.00s]  to sum over the final dimension,
[1814.00s -> 1817.00s]  and now you basically say,
[1817.00s -> 1820.00s]  actually, okay, so this replaces with sum.
[1820.00s -> 1825.00s]  So reduce, and again, you say hidden,
[1825.00s -> 1827.00s]  and hidden is disappeared,
[1827.00s -> 1832.00s]  which means that you are aggregating over that dimension.
[1832.00s -> 1834.00s]  Okay, so you can check that.
[1834.00s -> 1840.00s]  Indeed, kind of works over here.
[1840.00s -> 1846.00s]  Okay, so maybe one final example of this is
[1846.00s -> 1849.00s]  sometimes in a tensor,
[1849.00s -> 1852.00s]  one dimension actually represents multiple dimensions,
[1852.00s -> 1854.00s]  and you want to unpack that
[1854.00s -> 1856.00s]  and operate over one of them and pack it back.
[1856.00s -> 1861.00s]  So in this case, let's say you have batch sequence,
[1861.00s -> 1863.00s]  and then this eight-dimensional vector
[1863.00s -> 1866.00s]  is actually a flattened representation
[1866.00s -> 1870.00s]  of number of heads times some hidden dimension.
[1870.00s -> 1873.00s]  Okay, so and then you have a vector
[1873.00s -> 1877.00s]  that needs to operate on that hidden dimension.
[1877.00s -> 1882.00s]  So you can do this very elegantly using INOPs
[1882.00s -> 1886.00s]  by calling rearrange,
[1886.00s -> 1889.00s]  and this basically, you can think about it,
[1889.00s -> 1891.00s]  we saw a view before.
[1891.00s -> 1894.00s]  It's kind of like kind of a fancier version,
[1894.00s -> 1900.00s]  which basically looks at the same data, but differently.
[1900.00s -> 1902.00s]  So here it basically says
[1902.00s -> 1905.00s]  this dimension is actually heads in hidden one.
[1905.00s -> 1909.00s]  I'm gonna explode that into two dimensions.
[1909.00s -> 1915.00s]  And you have to specify the number of heads here
[1915.00s -> 1919.00s]  because there's multiple ways to split a number into two.
[1919.00s -> 1923.00s]  Let's see, this might be a little bit long.
[1923.00s -> 1927.00s]  Okay, maybe it's not worth looking at right now.
[1927.00s -> 1933.00s]  And given that X, you can perform your transformation
[1933.00s -> 1935.00s]  using line sum.
[1935.00s -> 1940.00s]  So this is something hidden one, which corresponds to X,
[1940.00s -> 1943.00s]  and then hidden one, hidden two, which corresponds to W,
[1943.00s -> 1947.00s]  and that gives you something hidden two.
[1948.00s -> 1950.00s]  Okay?
[1950.00s -> 1953.00s]  And then you can rearrange back.
[1953.00s -> 1956.00s]  So this is just the inverse of breaking up.
[1956.00s -> 1958.00s]  So you have your two dimensions
[1958.00s -> 1960.00s]  and you group it into one.
[1960.00s -> 1962.00s]  So that's just a flattening operation
[1962.00s -> 1965.00s]  that's with everything,
[1965.00s -> 1969.00s]  all the other dimensions kind of left alone.
[1971.00s -> 1975.00s]  Okay, so there is a tutorial for this
[1975.00s -> 1977.00s]  that I would recommend you go through
[1977.00s -> 1979.00s]  and it gives you a bit more.
[1979.00s -> 1981.00s]  So you don't have to use this
[1981.00s -> 1983.00s]  because you're building it from scratch
[1983.00s -> 1985.00s]  so you can kind of do anything you want,
[1985.00s -> 1988.00s]  but in assignment one we do give you guidance
[1988.00s -> 1992.00s]  and it's something probably to invest in.
[1996.00s -> 1997.00s]  Okay.
[1999.00s -> 2001.00s]  So now let's talk about
[2001.00s -> 2007.00s]  computation cost of tensor operations.
[2007.00s -> 2011.00s]  So we introduce a bunch of operations
[2011.00s -> 2014.00s]  and how much do they cost.
[2014.00s -> 2017.00s]  So a floating point operation
[2017.00s -> 2020.00s]  is any operation, floating point,
[2020.00s -> 2023.00s]  like addition or multiplication.
[2023.00s -> 2027.00s]  These are kind of the main ones
[2027.00s -> 2030.00s]  that are going to, I think, matter
[2030.00s -> 2032.00s]  in terms of flop count.
[2032.00s -> 2036.00s]  One thing that is sort of a pet peeve of mine
[2036.00s -> 2037.00s]  is that when you say flops,
[2037.00s -> 2039.00s]  it's actually unclear what you mean.
[2039.00s -> 2042.00s]  So you could mean flops with a lowercase s,
[2042.00s -> 2046.00s]  which stands for number of floating operations.
[2046.00s -> 2049.00s]  This measures amount of computation that you've done.
[2049.00s -> 2054.00s]  Or you could mean flops also written with an uppercase S,
[2054.00s -> 2056.00s]  which means floating points per second,
[2056.00s -> 2059.00s]  which is used to measure the speed of hardware.
[2059.00s -> 2064.00s]  So we're not going to, in this class, use uppercase S
[2064.00s -> 2066.00s]  because I find that very confusing
[2066.00s -> 2069.00s]  and just write slash s to denote
[2069.00s -> 2072.00s]  that it's a floating point per second.
[2072.00s -> 2073.00s]  Okay?
[2074.00s -> 2077.00s]  Okay, so just to give you some intuition about flops,
[2077.00s -> 2082.00s]  GPT-3 took about three 23 flops.
[2082.00s -> 2085.00s]  GPT-4 was two E 25 flops.
[2085.00s -> 2087.00s]  Speculation.
[2087.00s -> 2089.00s]  And there was a U.S. executive order
[2089.00s -> 2092.00s]  that any foundation model with over one E 26 flops
[2092.00s -> 2094.00s]  had to be reported to government,
[2094.00s -> 2098.00s]  which now has been revoked.
[2098.00s -> 2101.00s]  But the EU has still, they're going,
[2101.00s -> 2103.00s]  still has something that hasn't,
[2103.00s -> 2106.00s]  the EUAI Act, which is one E 25,
[2106.00s -> 2108.00s]  which hasn't been revoked.
[2109.00s -> 2113.00s]  So, you know, some intuitions,
[2113.00s -> 2118.00s]  A 100 has a peak performance of 312 teraflop per second.
[2121.00s -> 2124.00s]  And H 100 has a peak performance
[2124.00s -> 2129.00s]  of 1979 teraflop per second with sparsity
[2129.00s -> 2132.00s]  and approximately 50% without.
[2132.00s -> 2135.00s]  And if you look at, you know,
[2135.00s -> 2138.00s]  the NVIDIA has these specification sheets.
[2138.00s -> 2142.00s]  So you can see that the flops actually depends
[2142.00s -> 2144.00s]  on what you're trying to do.
[2144.00s -> 2148.00s]  So if you're using Fp32,
[2148.00s -> 2150.00s]  it's actually really, really bad.
[2150.00s -> 2154.00s]  Like if you run Fp32 on H 100,
[2154.00s -> 2158.00s]  you're not getting its orders of magnitude worse
[2158.00s -> 2161.00s]  than if you're doing Fp16
[2161.00s -> 2165.00s]  and if you're willing to go down to Fp8,
[2165.00s -> 2167.00s]  then it can be even faster.
[2167.00s -> 2170.00s]  And, you know, for the first one that I didn't realize,
[2170.00s -> 2173.00s]  but there's an asterisk here and this means with sparsity.
[2173.00s -> 2175.00s]  So usually you're in,
[2175.00s -> 2178.00s]  a lot of the matrices we have in this class are dense
[2178.00s -> 2180.00s]  so you don't actually get this.
[2180.00s -> 2182.00s]  You get something like, you know.
[2182.00s -> 2184.00s]  It's exactly half that number.
[2184.00s -> 2186.00s]  Exactly half, okay.
[2190.00s -> 2191.00s]  Okay, so,
[2193.00s -> 2196.00s]  so now you can do a bucket of calculations.
[2196.00s -> 2199.00s]  Eight H 100s for two weeks is
[2200.00s -> 2204.00s]  just eight times the number of flops per second
[2204.00s -> 2208.00s]  times the number of seconds in a week.
[2208.00s -> 2210.00s]  Actually this might be one week.
[2210.00s -> 2212.00s]  Okay, so that's one week.
[2212.00s -> 2216.00s]  And that's 4.7 times e to the 21,
[2217.00s -> 2220.00s]  which is, you know, some number.
[2220.00s -> 2223.00s]  And you can kind of contextualize the flop counts
[2223.00s -> 2225.00s]  with the other model counts.
[2227.00s -> 2228.00s]  Yeah.
[2228.00s -> 2231.00s]  So that means if, so what does sparsity mean?
[2231.00s -> 2234.00s]  That means if your matrices are sparse.
[2234.00s -> 2236.00s]  It's a specific, like, structure of sparsity.
[2236.00s -> 2238.00s]  It's like two out of four elements
[2238.00s -> 2241.00s]  in each, like, group of four elements is zero.
[2241.00s -> 2243.00s]  That's the only case where you get that speed.
[2243.00s -> 2245.00s]  No one uses it.
[2245.00s -> 2249.00s]  Yeah, it's a marketing department uses it.
[2252.00s -> 2253.00s]  Okay.
[2254.00s -> 2257.00s]  So let's go through a simple example.
[2257.00s -> 2259.00s]  So remember, we're not gonna touch the transformer,
[2259.00s -> 2261.00s]  but I think even a linear model gives us
[2261.00s -> 2264.00s]  a lot of the building blocks and intuitions.
[2264.00s -> 2267.00s]  So suppose we have end points.
[2267.00s -> 2269.00s]  Each point is d-dimensional.
[2269.00s -> 2271.00s]  And the linear model is just gonna match,
[2271.00s -> 2275.00s]  map each d-dimensional vector to a k-dimensional vector.
[2275.00s -> 2279.00s]  Okay, so let's set some number of points
[2279.00s -> 2283.00s]  is b, dimension is d, k is the number of outputs.
[2285.00s -> 2288.00s]  And let's create our data matrix, x,
[2288.00s -> 2293.00s]  our weight matrix, w.
[2293.00s -> 2296.00s]  And the linear model is just some matmul.
[2296.00s -> 2300.00s]  So nothing, you know, too interesting going on.
[2300.00s -> 2305.00s]  And, you know, the question is
[2305.00s -> 2308.00s]  how many flops was that?
[2308.00s -> 2313.00s]  And the way you would look at this is you say,
[2313.00s -> 2317.00s]  well, when you do the matrix multiplication,
[2317.00s -> 2322.00s]  you have basically for every i, j, k triple,
[2322.00s -> 2326.00s]  I have to multiply two numbers together.
[2326.00s -> 2332.00s]  And I also have to add that number to the total.
[2332.00s -> 2333.00s]  Okay?
[2333.00s -> 2338.00s]  So the answer is two times the,
[2338.00s -> 2341.00s]  basically the product of all the dimensions involved.
[2341.00s -> 2343.00s]  So the left dimension, the middle dimension,
[2343.00s -> 2346.00s]  and the right dimension.
[2346.00s -> 2347.00s]  Okay?
[2347.00s -> 2350.00s]  So this is something that you should just kind of remember.
[2350.00s -> 2352.00s]  If you're doing a matrix multiplication,
[2352.00s -> 2355.00s]  the number of flops is two times
[2355.00s -> 2358.00s]  the product of the three dimensions.
[2359.00s -> 2361.00s]  Okay?
[2361.00s -> 2364.00s]  So the flops of other operations are,
[2364.00s -> 2370.00s]  usually you can linear in the size of the matrix or tensor.
[2370.00s -> 2373.00s]  And in general, no other operation you encounter
[2373.00s -> 2377.00s]  in deep learning is as expensive as matrix multiplication
[2377.00s -> 2379.00s]  for large enough matrices.
[2379.00s -> 2382.00s]  So this is why I think a lot of the napkin math
[2382.00s -> 2385.00s]  is very simple because we're only looking at
[2385.00s -> 2390.00s]  the matrix multiplications that are performed by the model.
[2391.00s -> 2393.00s]  Now of course there are regimes
[2393.00s -> 2396.00s]  where if your matrices are small enough,
[2396.00s -> 2398.00s]  then the cost of other things starts to dominate.
[2398.00s -> 2401.00s]  But generally that's not a good regime you want to be in
[2401.00s -> 2403.00s]  because the hardware is designed for
[2403.00s -> 2405.00s]  big, much versus multiplication.
[2405.00s -> 2408.00s]  So sort of by, it's a little bit circular,
[2408.00s -> 2410.00s]  but by kind of, we end up in this regime
[2410.00s -> 2413.00s]  where we only consider models
[2413.00s -> 2417.00s]  where the mat models are the dominant cost.
[2419.00s -> 2420.00s]  Okay.
[2420.00s -> 2423.00s]  Any questions about this number?
[2423.00s -> 2426.00s]  Two times the product of the three dimensions.
[2426.00s -> 2428.00s]  This is just a useful thing.
[2428.00s -> 2430.00s]  Would the algorithm of matrix multiplication
[2430.00s -> 2431.00s]  always be the same?
[2431.00s -> 2434.00s]  Because the chip might have optimized that.
[2434.00s -> 2437.00s]  They're always correlated the same.
[2439.00s -> 2441.00s]  Yeah, so the question is like,
[2442.00s -> 2444.00s]  does this, essentially does this depend
[2444.00s -> 2447.00s]  on the matrix multiplication algorithm?
[2449.00s -> 2454.00s]  In general, I guess we'll look at this next week
[2454.00s -> 2456.00s]  or the week after when we look at kernels.
[2456.00s -> 2459.00s]  I mean actually there's a lot of optimization
[2459.00s -> 2461.00s]  that goes underneath, under the hood
[2461.00s -> 2464.00s]  when it comes to matrix multiplications.
[2464.00s -> 2466.00s]  And there's a lot of specialization
[2466.00s -> 2468.00s]  depending on the shape.
[2468.00s -> 2470.00s]  So this is, I would say this is just
[2470.00s -> 2473.00s]  a kind of a crude estimate
[2473.00s -> 2478.00s]  that is basically like the right order of magnitude.
[2483.00s -> 2485.00s]  Okay, so, yeah.
[2485.00s -> 2488.00s]  Additions and multiplications are considered equivalent?
[2488.00s -> 2490.00s]  Yeah, additions and multiplications
[2490.00s -> 2492.00s]  are considered equivalent.
[2494.00s -> 2497.00s]  So one way I find helpful to interpret this,
[2498.00s -> 2499.00s]  so at the end of the day,
[2499.00s -> 2501.00s]  this is just a matrix multiplication.
[2501.00s -> 2505.00s]  But I'm gonna try to give a little bit of meaning to this
[2505.00s -> 2507.00s]  which is why I've set up this
[2507.00s -> 2509.00s]  as kind of a little toy machine learning problem.
[2509.00s -> 2514.00s]  So B is really stands for the number of data points
[2514.00s -> 2517.00s]  and dk is the number of parameters.
[2517.00s -> 2519.00s]  So for this particular model,
[2519.00s -> 2522.00s]  the number of flops that's required for forward pass
[2522.00s -> 2524.00s]  is two times the number of tokens
[2524.00s -> 2528.00s]  or the number of data points times the number of parameters.
[2528.00s -> 2532.00s]  So this turns out to actually generalize to transformers.
[2532.00s -> 2535.00s]  There's an asterisk there because
[2537.00s -> 2539.00s]  there's the sequence length and other stuff,
[2539.00s -> 2542.00s]  but this is roughly right
[2542.00s -> 2546.00s]  if your sequence length isn't too large.
[2546.00s -> 2551.00s]  So, okay, so now this is just
[2554.00s -> 2558.00s]  the number of floating point operations, right?
[2558.00s -> 2561.00s]  So how does this actually translate to a walk-like time
[2561.00s -> 2564.00s]  which is presumably the thing you actually care about?
[2564.00s -> 2567.00s]  How long do you have to wait for your run?
[2567.00s -> 2570.00s]  So let's time this.
[2570.00s -> 2574.00s]  So I have this function that is just going to
[2576.00s -> 2580.00s]  do it five times,
[2580.00s -> 2584.00s]  and I'm going to perform the matrix multiply operation.
[2584.00s -> 2587.00s]  We'll talk a little bit later about this
[2587.00s -> 2591.00s]  two weeks from now, why the other code is here.
[2591.00s -> 2595.00s]  But for now, we get an actual time.
[2595.00s -> 2600.00s]  So that matrix took 0.16 seconds.
[2600.00s -> 2604.00s]  And the actual flops per second,
[2604.00s -> 2607.00s]  which is how many flops did it do per second,
[2607.00s -> 2611.00s]  is 5.4E13.
[2611.00s -> 2613.00s]  Okay?
[2613.00s -> 2618.00s]  So now you can compare this with the marketing materials
[2618.00s -> 2622.00s]  for the A100 and H100.
[2622.00s -> 2625.00s]  And as we look at the spec sheet,
[2625.00s -> 2628.00s]  the flops depends on the data type,
[2628.00s -> 2633.00s]  and we see that the promise flops per second
[2633.00s -> 2641.00s]  which for H100, for, I guess this is for float 32,
[2641.00s -> 2647.00s]  is 67 teraflops, as we looked.
[2647.00s -> 2655.00s]  And so that is the number of promise flops per second we had.
[2655.00s -> 2659.00s]  And now, if you look at the,
[2659.00s -> 2664.00s]  there's a helpful notion called model flops utilization, or MFU,
[2664.00s -> 2669.00s]  which is the actual number of flops divided by the promise flops.
[2669.00s -> 2670.00s]  Okay?
[2670.00s -> 2671.00s]  So you take the actual number of flops,
[2671.00s -> 2675.00s]  remember which is what you actually witnessed,
[2675.00s -> 2682.00s]  the number of floating point operations that are useful for your model,
[2682.00s -> 2685.00s]  divided by the actual time it took,
[2685.00s -> 2687.00s]  divided by this promise flops per second,
[2687.00s -> 2690.00s]  which is from the glossy brochure,
[2690.00s -> 2695.00s]  you can get a MFU of .8.
[2695.00s -> 2697.00s]  Okay?
[2697.00s -> 2701.00s]  So usually you see people talking about their MFUs,
[2701.00s -> 2707.00s]  and something greater than .5 is usually considered to be good,
[2707.00s -> 2711.00s]  and if you're like 5% MFU, that's considered to be really bad.
[2711.00s -> 2719.00s]  You usually can't get close to, that close to, you know, 90 or 100,
[2719.00s -> 2723.00s]  because this is sort of ignoring all sort of communication overhead,
[2723.00s -> 2728.00s]  it's just like the literal computation of a flops.
[2728.00s -> 2731.00s]  Okay, and usually MFU is much higher
[2731.00s -> 2735.00s]  if the matrix multiplications dominate.
[2735.00s -> 2737.00s]  Okay, so that's MFU.
[2737.00s -> 2740.00s]  Any questions about this?
[2740.00s -> 2741.00s]  Yeah?
[2741.00s -> 2744.00s]  You're using the promise flop per sec,
[2744.00s -> 2746.00s]  not considering the sparse.
[2746.00s -> 2755.00s]  So this promise flop per sec is not considering the sparse.
[2755.00s -> 2759.00s]  One note is that this is actually, you know,
[2759.00s -> 2763.00s]  there's also something called hardware flop serialization,
[2763.00s -> 2772.00s]  and the motivation here is that we're trying to look at the,
[2772.00s -> 2777.00s]  it's called model because we're looking at the number of effective,
[2777.00s -> 2781.00s]  useful operations that the model is, you know, performing.
[2781.00s -> 2782.00s]  Okay?
[2782.00s -> 2785.00s]  And so it's a way of kind of standardizing.
[2785.00s -> 2789.00s]  It's not the actual number of flops that are done,
[2789.00s -> 2792.00s]  because you could have optimization in your code
[2792.00s -> 2796.00s]  that cache a few things or redo, you know,
[2796.00s -> 2798.00s]  recomputation of some things,
[2798.00s -> 2802.00s]  and in some sense, you're still computing the same model.
[2802.00s -> 2805.00s]  So what matters is that this is sort of trying
[2805.00s -> 2806.00s]  to look at the model complexity,
[2806.00s -> 2809.00s]  and you shouldn't be penalized just because you were clever
[2809.00s -> 2811.00s]  in your MFU if you were clever
[2811.00s -> 2814.00s]  and you didn't actually do the flops,
[2814.00s -> 2817.00s]  but you said you did.
[2817.00s -> 2823.00s]  Okay, so you can also do the same with BF16.
[2823.00s -> 2824.00s]  Oops.
[2824.00s -> 2830.00s]  And here, we see that for BF,
[2830.00s -> 2835.00s]  the time is actually much better, right?
[2835.00s -> 2839.00s]  So .03 instead of .16,
[2839.00s -> 2844.00s]  so the actual flops per second is higher.
[2844.00s -> 2846.00s]  Even accounting for sparsity,
[2846.00s -> 2849.00s]  the promise flops is still quite high,
[2849.00s -> 2856.00s]  so the MFU is actually lower for BF16.
[2856.00s -> 2862.00s]  This is maybe surprisingly low,
[2862.00s -> 2868.00s]  but sometimes the promise flops is a bit optimistic.
[2868.00s -> 2871.00s]  So always benchmark your code,
[2871.00s -> 2872.00s]  and don't just kind of assume
[2872.00s -> 2876.00s]  that you're gonna get certain levels of performance.
[2876.00s -> 2880.00s]  Okay, so just to summarize,
[2880.00s -> 2885.00s]  matrix multiplications dominate the compute,
[2885.00s -> 2887.00s]  and the general rule of thumb is that
[2887.00s -> 2893.00s]  it's two times the product of the dimensions, flops.
[2893.00s -> 2896.00s]  The flops per second,
[2896.00s -> 2898.00s]  floating points per second,
[2898.00s -> 2903.00s]  depends on the hardware and also the data type.
[2903.00s -> 2905.00s]  So the fancier the hardware you have,
[2905.00s -> 2907.00s]  the higher it is.
[2907.00s -> 2909.00s]  The smaller the data type,
[2909.00s -> 2912.00s]  usually the faster it is.
[2912.00s -> 2915.00s]  And MFU is a useful notion
[2915.00s -> 2924.00s]  to look at how well you're essentially squeezing your hardware.
[2924.00s -> 2925.00s]  Yeah?
[2925.00s -> 2926.00s]  I've heard that often,
[2926.00s -> 2928.00s]  in order to get the maximum utilization,
[2928.00s -> 2931.00s]  you want to use these tensor cores on the machine,
[2931.00s -> 2935.00s]  and so does PyTorch by default use these tensor cores?
[2935.00s -> 2938.00s]  Are these tensor cores accounting for that?
[2938.00s -> 2942.00s]  Yeah, so the question is, what about those tensor cores?
[2942.00s -> 2947.00s]  So if you go to this spec sheet,
[2947.00s -> 2954.00s]  you'll see that these are all on the tensor core.
[2954.00s -> 2957.00s]  So the tensor core is basically a specialized hardware
[2957.00s -> 2960.00s]  to do matmalls.
[2960.00s -> 2969.00s]  So if you are, so by default it should use it,
[2969.00s -> 2972.00s]  and especially if you're using PyTorch compile,
[2972.00s -> 2978.00s]  it will generate the code that will use the hardware properly.
[2984.00s -> 2989.00s]  Okay, so let's talk a little bit about gradients.
[2989.00s -> 2992.00s]  And the reason is that we've only looked
[2992.00s -> 2995.00s]  at matrix multiplication, or in other words,
[2995.00s -> 2998.00s]  basically feed-forward, forward passes,
[2998.00s -> 3000.00s]  and the number of flops.
[3000.00s -> 3001.00s]  But there's also a computation
[3001.00s -> 3003.00s]  that comes from computing gradients,
[3003.00s -> 3007.00s]  and we want to track down how much that is.
[3007.00s -> 3012.00s]  Okay, so just to consider a simple example,
[3012.00s -> 3015.00s]  a simple linear model,
[3015.00s -> 3018.00s]  where you take the prediction of a linear model
[3018.00s -> 3023.00s]  and you look at the MSE with respect to five.
[3023.00s -> 3025.00s]  So, not a very interesting loss,
[3025.00s -> 3031.00s]  but I think it's illustrative for looking at the gradients.
[3031.00s -> 3033.00s]  Okay, so remember in the forward pass,
[3033.00s -> 3036.00s]  you have your x, you have your w,
[3036.00s -> 3040.00s]  which you want to compute the gradient with respect to,
[3040.00s -> 3044.00s]  you make a prediction by taking a linear product,
[3044.00s -> 3049.00s]  and then you have your loss, okay?
[3049.00s -> 3053.00s]  And in the backward pass, you just call loss backwards,
[3053.00s -> 3058.00s]  and in this case, the gradient,
[3058.00s -> 3061.00s]  which is this variable attached to the tensor,
[3061.00s -> 3066.00s]  turns out to be what you want, okay?
[3066.00s -> 3073.00s]  So everyone has done gradients in PyTorch before.
[3073.00s -> 3077.00s]  So let's look at how many flops are required
[3077.00s -> 3081.00s]  for computing gradients.
[3081.00s -> 3090.00s]  Okay, so let's look at a slightly more complicated model.
[3090.00s -> 3095.00s]  So now it's a two-layer linear model,
[3095.00s -> 3098.00s]  where you have x, which is d by d,
[3098.00s -> 3105.00s]  times w1, which is d by d, so that's the first layer,
[3105.00s -> 3109.00s]  and then you take your hidden activations, h1,
[3109.00s -> 3113.00s]  and you pass it through another linear layer, w2,
[3113.00s -> 3115.00s]  and to get a k-dimensional vector,
[3115.00s -> 3120.00s]  and you do some, compute some loss.
[3120.00s -> 3123.00s]  Okay, so this is a two-layer linear network,
[3123.00s -> 3125.00s]  and just as a kind of review,
[3125.00s -> 3129.00s]  if you look at the number of forward flops,
[3129.00s -> 3133.00s]  what you had to do was, you have to multiply,
[3133.00s -> 3138.00s]  look at w1, you have to multiply x by w1,
[3138.00s -> 3142.00s]  and add it to your h1,
[3142.00s -> 3145.00s]  and you have to take h1 and w2,
[3145.00s -> 3149.00s]  and you have to add it to your h2.
[3149.00s -> 3152.00s]  Okay, so the total number of flops, again,
[3152.00s -> 3155.00s]  is two times the product of all the dimensions
[3155.00s -> 3159.00s]  in your matmul, plus two times the product dimensions
[3159.00s -> 3161.00s]  in your matmul for the second matrix.
[3161.00s -> 3162.00s]  Okay, in other words,
[3162.00s -> 3166.00s]  two times the total number of parameters in this case.
[3166.00s -> 3170.00s]  Okay, so what about the backward pass?
[3170.00s -> 3175.00s]  So this part will be a little bit more involved.
[3175.00s -> 3181.00s]  So we can recall the model x to h1 to h2 and the loss.
[3181.00s -> 3182.00s]  So in the backward pass,
[3182.00s -> 3185.00s]  you have to compute a bunch of gradients.
[3185.00s -> 3187.00s]  And the gradients that are relevant
[3187.00s -> 3190.00s]  is you have to compute the gradient
[3190.00s -> 3202.00s]  with respect to h1, h2, w1, and w2 of the loss.
[3202.00s -> 3205.00s]  So d loss, each of these variables.
[3205.00s -> 3208.00s]  Okay, so how long does it take to compute that?
[3208.00s -> 3211.00s]  Let's just look at w2 for now.
[3211.00s -> 3215.00s]  Okay, so the things that touch w2,
[3215.00s -> 3219.00s]  you can compute by looking at the chain rule.
[3219.00s -> 3227.00s]  So w2 grad, so the gradient of d loss, dw2,
[3227.00s -> 3236.00s]  is you sum h1 times the gradient
[3236.00s -> 3240.00s]  of the loss with respect to h2.
[3240.00s -> 3241.00s]  Okay?
[3241.00s -> 3245.00s]  So that's just the chain rule for w2.
[3245.00s -> 3251.00s]  And this is, so all the gradients are the same size
[3251.00s -> 3256.00s]  as the underlying vectors.
[3256.00s -> 3260.00s]  So this turns out to be,
[3260.00s -> 3264.00s]  it essentially looks like a matrix multiplication.
[3264.00s -> 3267.00s]  And so the same calculus holds,
[3267.00s -> 3272.00s]  which is that it's two times the number of,
[3272.00s -> 3274.00s]  the product of all the dimensions,
[3274.00s -> 3277.00s]  times d times k.
[3277.00s -> 3278.00s]  Okay?
[3278.00s -> 3283.00s]  But this is only the gradient with respect to w2.
[3283.00s -> 3287.00s]  We also need to compute the gradient with respect to h1
[3287.00s -> 3293.00s]  because we have to keep on back propagating to w1 and so on.
[3293.00s -> 3308.00s]  Okay, so that is going to be the product of w2 times h2.
[3308.00s -> 3314.00s]  Sorry, I think this should be that grad of h2, h2.grad.
[3314.00s -> 3318.00s]  So that turns out to also be essentially,
[3318.00s -> 3322.00s]  looks like the matrix multiplication
[3322.00s -> 3325.00s]  and it's the same number of flops
[3325.00s -> 3331.00s]  for computing the gradient of h1.
[3331.00s -> 3333.00s]  Okay, so when you add the two,
[3333.00s -> 3336.00s]  so that's just for w2.
[3336.00s -> 3338.00s]  You do the same thing for w1,
[3338.00s -> 3341.00s]  and that's, which has d times d parameters.
[3341.00s -> 3345.00s]  And when you add it all up,
[3345.00s -> 3350.00s]  it's, so for this, for w2,
[3350.00s -> 3355.00s]  the amount of computation was four times b times d times k.
[3355.00s -> 3362.00s]  And for w1, it's also four times b times d times d
[3362.00s -> 3367.00s]  because w1 is d by d.
[3367.00s -> 3369.00s]  Okay?
[3369.00s -> 3373.00s]  So, I know there's a lot of symbols here.
[3373.00s -> 3377.00s]  I'm gonna try also to give you a visual account for this.
[3377.00s -> 3383.00s]  So this is from a blog post that I think may work better.
[3383.00s -> 3384.00s]  We'll see.
[3384.00s -> 3387.00s]  Okay, I have to wait for the animation to loop back.
[3387.00s -> 3390.00s]  So basically this is one layer of the neural network
[3390.00s -> 3394.00s]  where it has the hidden and then the weights
[3394.00s -> 3395.00s]  to the next layer.
[3395.00s -> 3398.00s]  And so I have to, okay,
[3398.00s -> 3402.00s]  the problem with this animation is I have to wait.
[3402.00s -> 3404.00s]  Okay, ready, set, okay.
[3404.00s -> 3408.00s]  Okay, so first I have to multiply w and a
[3408.00s -> 3410.00s]  and I have to add it to this.
[3410.00s -> 3411.00s]  That's a forward pass.
[3411.00s -> 3413.00s]  And now I'm gonna multiply this, these two,
[3413.00s -> 3415.00s]  and then add it to that.
[3415.00s -> 3418.00s]  And I'm gonna multiply and then add it to that.
[3418.00s -> 3419.00s]  Okay.
[3419.00s -> 3423.00s]  Any questions?
[3423.00s -> 3427.00s]  I wish there were a way to slow this down.
[3427.00s -> 3431.00s]  But, you know, the details maybe I'll let you kind of
[3431.00s -> 3434.00s]  ruminate on, but the high level is that there's
[3434.00s -> 3437.00s]  two times the number of parameters for the forward pass
[3437.00s -> 3439.00s]  and four times the number of parameters
[3439.00s -> 3440.00s]  for the backward pass.
[3440.00s -> 3443.00s]  And we can just kind of work it out
[3443.00s -> 3444.00s]  via the chain rule here.
[3444.00s -> 3445.00s]  Yeah.
[3445.00s -> 3448.00s]  For the homeworks, are we also using the,
[3448.00s -> 3450.00s]  you said some type of implementation is allowed,
[3450.00s -> 3451.00s]  some isn't.
[3451.00s -> 3455.00s]  Are we allowed to use that or are we doing the,
[3455.00s -> 3459.00s]  like entirely by hand to integrate it?
[3459.00s -> 3461.00s]  So the question is, in the homework,
[3461.00s -> 3463.00s]  are you going to compute gradients by hand?
[3463.00s -> 3464.00s]  And the answer is no.
[3464.00s -> 3467.00s]  You're going to just use pi torch gradient.
[3467.00s -> 3469.00s]  This is just to break it down
[3469.00s -> 3473.00s]  so we can do the counting flops.
[3475.00s -> 3479.00s]  Okay, any questions about this before I move on?
[3485.00s -> 3487.00s]  Okay, just to summarize,
[3487.00s -> 3490.00s]  the forward pass is, for this particular model,
[3490.00s -> 3493.00s]  is two times the number of data points
[3493.00s -> 3495.00s]  times the number of parameters,
[3495.00s -> 3497.00s]  and backwards is four times the number of data points
[3497.00s -> 3499.00s]  times the number of parameters,
[3499.00s -> 3501.00s]  which means that total is six times the number of data
[3501.00s -> 3503.00s]  times parameters.
[3503.00s -> 3507.00s]  Okay, and that explains why there was that six
[3507.00s -> 3511.00s]  in the beginning when I asked the motivating question.
[3511.00s -> 3516.00s]  So now this is for a simple, you know, linear model.
[3516.00s -> 3518.00s]  It turns out that many models,
[3518.00s -> 3522.00s]  this is basically the bulk of the computation
[3522.00s -> 3528.00s]  when essentially every computation you do has,
[3528.00s -> 3533.00s]  you know, touches essentially a new parameter, roughly.
[3533.00s -> 3536.00s]  And, you know, obviously this doesn't hold,
[3536.00s -> 3538.00s]  you can find models where this doesn't hold
[3538.00s -> 3539.00s]  because you can have like one parameter
[3539.00s -> 3543.00s]  through parameter sharing and have a billion flops,
[3543.00s -> 3547.00s]  but that's generally not what models look like.
[3549.00s -> 3551.00s]  Okay, so let me move on.
[3556.00s -> 3560.00s]  So far I've basically finished talking
[3560.00s -> 3562.00s]  about the resource accounting.
[3562.00s -> 3563.00s]  So we looked at tensors,
[3563.00s -> 3565.00s]  we looked at some computation on tensors,
[3565.00s -> 3569.00s]  we looked at how much tensors take to store
[3569.00s -> 3573.00s]  and also how many flops tensors take
[3573.00s -> 3576.00s]  when you do various operations on them.
[3576.00s -> 3580.00s]  Now let's start building up different models.
[3580.00s -> 3584.00s]  I think this part isn't necessarily going to be,
[3584.00s -> 3589.00s]  you know, that's conceptually interesting or challenging,
[3589.00s -> 3593.00s]  but it's more for maybe just, you know, completeness.
[3593.00s -> 3599.00s]  Okay, so parameters in PyTorch are stored
[3599.00s -> 3604.00s]  as these nn parameter objects.
[3604.00s -> 3609.00s]  Let's talk a little bit about parameter initialization.
[3609.00s -> 3619.00s]  So if you have, let's say, a parameter that has,
[3619.00s -> 3623.00s]  okay, so you generate, okay, sorry,
[3623.00s -> 3625.00s]  your w parameter is an input dimension
[3625.00s -> 3628.00s]  by hidden dimension matrix.
[3628.00s -> 3630.00s]  You're still in the linear model case,
[3630.00s -> 3631.00s]  so let's just turn in an input
[3631.00s -> 3634.00s]  and let's feed it through the output.
[3634.00s -> 3641.00s]  Okay, so rand n unit of Gaussian seems innocuous.
[3641.00s -> 3643.00s]  What happens when you do this
[3643.00s -> 3645.00s]  is that if you look at the output,
[3645.00s -> 3648.00s]  you get some pretty large numbers, right?
[3648.00s -> 3654.00s]  And this is because when you have the number grows
[3654.00s -> 3658.00s]  as essentially the square root of the hidden dimension,
[3658.00s -> 3661.00s]  and so when you have large models,
[3661.00s -> 3663.00s]  this is going to blow up.
[3663.00s -> 3668.00s]  And training can be very unstable.
[3668.00s -> 3673.00s]  So typically what you want to do is initialize
[3673.00s -> 3676.00s]  in a way that's invariant to hidden,
[3676.00s -> 3678.00s]  or at least when you're guaranteed
[3678.00s -> 3680.00s]  that it's not going to blow up.
[3680.00s -> 3682.00s]  And one simple way to do this
[3682.00s -> 3685.00s]  is just rescale by the one over square root
[3685.00s -> 3689.00s]  of number of inputs.
[3689.00s -> 3692.00s]  So basically let's redo this.
[3692.00s -> 3695.00s]  W equals a parameter where I simply divide
[3695.00s -> 3700.00s]  by the square root of the input dimension.
[3700.00s -> 3703.00s]  And then now when you feed it through the output,
[3703.00s -> 3706.00s]  now you get things that are stable around,
[3706.00s -> 3713.00s]  this will actually concentrate to something like normal zero one.
[3713.00s -> 3716.00s]  Okay, so this is basically,
[3716.00s -> 3718.00s]  this has been explored pretty extensively
[3718.00s -> 3720.00s]  in deep learning literature.
[3720.00s -> 3724.00s]  It's known up to a constant as savior initialization.
[3724.00s -> 3727.00s]  And typically I guess it's fairly common
[3727.00s -> 3729.00s]  if you want to be extra safe.
[3729.00s -> 3730.00s]  You don't trust the normal
[3730.00s -> 3733.00s]  because it doesn't have, it has unbounded tails.
[3733.00s -> 3735.00s]  And you say, I'm going to truncate to minus three three
[3735.00s -> 3737.00s]  so I don't get any large values
[3737.00s -> 3741.00s]  and I don't want any to mess with that.
[3741.00s -> 3746.00s]  Okay.
[3746.00s -> 3750.00s]  Okay, so.
[3750.00s -> 3756.00s]  So let's build just a simple model.
[3756.00s -> 3761.00s]  It's going to have d dimensions and two layers.
[3761.00s -> 3764.00s]  There's this, I just made up this name, Cruncher.
[3764.00s -> 3768.00s]  It's a custom model which is a deep linear network
[3768.00s -> 3772.00s]  which has n num layers layers
[3772.00s -> 3777.00s]  and each layer is a linear model
[3777.00s -> 3781.00s]  which has essentially just a matrix multiplication.
[3781.00s -> 3783.00s]  Okay.
[3783.00s -> 3788.00s]  So the parameters of this model
[3788.00s -> 3797.00s]  looks like I have layers for the first layer
[3797.00s -> 3800.00s]  which is a d by d matrix.
[3800.00s -> 3802.00s]  The second layer which is also a d by d matrix
[3802.00s -> 3807.00s]  and then I have a head or a final layer.
[3807.00s -> 3812.00s]  Okay, so if I get the number of parameters
[3812.00s -> 3816.00s]  of this model, then it's going to be
[3816.00s -> 3819.00s]  d squared plus d squared plus d.
[3819.00s -> 3823.00s]  Okay, so nothing too surprising there.
[3823.00s -> 3825.00s]  And I'm going to move it to the GPU
[3825.00s -> 3828.00s]  because I want this to run fast.
[3828.00s -> 3831.00s]  And I'm going to generate some random data
[3831.00s -> 3833.00s]  and feed it through the data
[3833.00s -> 3838.00s]  and the forward pass is just going through the layers
[3838.00s -> 3841.00s]  and then finally applying the head.
[3844.00s -> 3848.00s]  Okay, so with that model, let's try to,
[3848.00s -> 3851.00s]  I'm going to use this model and do some stuff with it.
[3851.00s -> 3855.00s]  But just one kind of general digression.
[3855.00s -> 3860.00s]  Randomness is something that is sort of,
[3860.00s -> 3862.00s]  can be annoying in some cases
[3862.00s -> 3865.00s]  if you're trying to reproduce a bug, for example.
[3865.00s -> 3866.00s]  It shows up in many places,
[3866.00s -> 3869.00s]  initialization, dropout, data ordering.
[3869.00s -> 3872.00s]  And just the best practices,
[3872.00s -> 3877.00s]  we recommend you always pass a fix of random seed
[3877.00s -> 3879.00s]  so you can reproduce your model
[3879.00s -> 3883.00s]  or at least as well as you can.
[3883.00s -> 3886.00s]  And in particular, having a different random seed
[3886.00s -> 3890.00s]  for every source of randomness is nice
[3890.00s -> 3891.00s]  because then you can, for example,
[3891.00s -> 3894.00s]  fix initialization or fix the data ordering
[3894.00s -> 3896.00s]  but very other things.
[3896.00s -> 3900.00s]  Determinism is your friend when you're debugging.
[3900.00s -> 3905.00s]  And in code, unfortunately there's many places
[3905.00s -> 3907.00s]  where you can use randomness
[3907.00s -> 3911.00s]  and just be cognizant of which one you're using
[3911.00s -> 3914.00s]  and just if you want to be safe,
[3914.00s -> 3917.00s]  just set the seed to for all of them.
[3919.00s -> 3923.00s]  Data loading, I guess I'll go through this quickly.
[3924.00s -> 3928.00s]  It's not, it'll be useful for your assignment.
[3930.00s -> 3932.00s]  So in language modeling,
[3932.00s -> 3934.00s]  data is typically just a sequence of integers
[3934.00s -> 3938.00s]  because this is, remember, output by the tokenizer
[3938.00s -> 3941.00s]  and you serialize them into,
[3941.00s -> 3945.00s]  you can serialize them into NumPy arrays.
[3945.00s -> 3949.00s]  And one, I guess, thing that's maybe useful
[3949.00s -> 3953.00s]  is that you don't want to load all your data
[3953.00s -> 3956.00s]  into memory at once because, for example,
[3956.00s -> 3959.00s]  the llama data is 2.8 terabytes.
[3959.00s -> 3962.00s]  But you can sort of pretend to load it
[3962.00s -> 3965.00s]  by using this handy function called memmap
[3965.00s -> 3968.00s]  which gives you essentially a variable
[3968.00s -> 3970.00s]  that is mapped to a file.
[3970.00s -> 3974.00s]  So when you try to access the data,
[3974.00s -> 3978.00s]  it actually on demand loads the file.
[3978.00s -> 3982.00s]  And then using that, you can create a data loader
[3982.00s -> 3989.00s]  that samples data from your batch.
[3989.00s -> 3993.00s]  So I'm gonna skip over that just in the interest of time.
[3993.00s -> 3996.00s]  Let's talk a little bit about optimizers.
[3996.00s -> 3999.00s]  So we've defined our model.
[4002.00s -> 4005.00s]  So there's many optimizers.
[4005.00s -> 4008.00s]  Just kind of maybe going through
[4008.00s -> 4010.00s]  the intuition behind some of them.
[4010.00s -> 4012.00s]  So of course there's stochastic gradient descent.
[4012.00s -> 4014.00s]  You compute the gradient of your batch.
[4014.00s -> 4015.00s]  You take a step in that direction.
[4015.00s -> 4017.00s]  No questions asked.
[4017.00s -> 4019.00s]  There's an idea called momentum
[4019.00s -> 4023.00s]  which dates back to classic optimization, Nesterov,
[4023.00s -> 4029.00s]  where you have a running average of your gradients
[4029.00s -> 4033.00s]  and you update against the running average
[4033.00s -> 4036.00s]  instead of your instantaneous gradient.
[4036.00s -> 4039.00s]  And then you have Adagrad
[4039.00s -> 4043.00s]  which you scale the gradients
[4043.00s -> 4054.00s]  by the square of the gradients.
[4054.00s -> 4056.00s]  You also have RMSprop
[4056.00s -> 4059.00s]  which is an improved version of Adagrad
[4059.00s -> 4061.00s]  which uses exponential averaging
[4061.00s -> 4064.00s]  rather than just like a flat average.
[4064.00s -> 4067.00s]  And then finally Adam which appeared in 2014
[4067.00s -> 4071.00s]  which is essentially combining RMSprop and momentum.
[4071.00s -> 4074.00s]  So that's why you're maintaining both
[4074.00s -> 4077.00s]  your running average of your gradients
[4077.00s -> 4080.00s]  but also running average of your gradients squared.
[4080.00s -> 4086.00s]  Okay, so since you're gonna implement Adam in homework one
[4086.00s -> 4087.00s]  I'm not gonna do that.
[4087.00s -> 4091.00s]  Instead I'm gonna implement Adagrad.
[4091.00s -> 4098.00s]  So the way you implement an optimizer in PyTorch
[4098.00s -> 4100.00s]  is that you override the optimizer class
[4100.00s -> 4105.00s]  and you have to, let's see,
[4105.00s -> 4108.00s]  maybe I'll get to the implementation
[4108.00s -> 4110.00s]  once we step through it.
[4110.00s -> 4115.00s]  So let's define some data,
[4115.00s -> 4119.00s]  compute the forward pass on the loss
[4119.00s -> 4122.00s]  and then you compute the gradients
[4122.00s -> 4127.00s]  and then when you call optimizer.step
[4127.00s -> 4132.00s]  this is where the optimizer actually is active.
[4132.00s -> 4135.00s]  So what this looks like is
[4135.00s -> 4139.00s]  your parameters are grouped by,
[4139.00s -> 4142.00s]  for example you have one for the layer zero, layer one
[4142.00s -> 4146.00s]  and then the final weights.
[4146.00s -> 4152.00s]  And you can access a state which is a dictionary
[4152.00s -> 4157.00s]  from parameters to whatever you want to store
[4157.00s -> 4160.00s]  as the optimizer state.
[4160.00s -> 4163.00s]  The gradient of that parameter you assume
[4163.00s -> 4169.00s]  is already calculated by the backward pass.
[4169.00s -> 4175.00s]  And now you can do things like in Adagrad
[4175.00s -> 4179.00s]  you're storing the sum of the gradient squareds.
[4179.00s -> 4182.00s]  So you can get that G2 variable
[4182.00s -> 4186.00s]  and you can update that based on the square of the gradient.
[4186.00s -> 4190.00s]  So this is element wise squaring of the gradient
[4190.00s -> 4193.00s]  and you put it back into the state.
[4193.00s -> 4196.00s]  So then obviously your optimizer is responsible
[4196.00s -> 4198.00s]  for updating the parameters
[4198.00s -> 4201.00s]  and this is just, you update the learning rate
[4201.00s -> 4205.00s]  times the gradient divided by this scaling.
[4205.00s -> 4208.00s]  So now this state is kept over
[4208.00s -> 4217.00s]  across multiple invocations of the optimizer.
[4217.00s -> 4223.00s]  Okay, so, and then at the end of your optimizer step
[4223.00s -> 4228.00s]  you can free up the memory just to,
[4228.00s -> 4231.00s]  which is I think going to actually be more important
[4231.00s -> 4235.00s]  when you look, when we talk about model parallelism.
[4235.00s -> 4238.00s]  Okay, so let's talk about the memory requirements
[4238.00s -> 4242.00s]  of the optimizer states.
[4242.00s -> 4244.00s]  And actually basically at this point everything.
[4244.00s -> 4250.00s]  So, you need to, the number of parameters in this model
[4250.00s -> 4253.00s]  is D squared times the number of layers
[4253.00s -> 4260.00s]  plus D for the final head, okay.
[4260.00s -> 4263.00s]  The number of activations,
[4263.00s -> 4265.00s]  so this is something we didn't do before
[4265.00s -> 4268.00s]  but now for this simple model it's fairly easy to do.
[4268.00s -> 4275.00s]  It's just B times D times the number of layers you have.
[4275.00s -> 4277.00s]  For every layer, for every data point,
[4277.00s -> 4281.00s]  for every dimension you have to hold the activations.
[4281.00s -> 4285.00s]  For the gradients, this is the same
[4285.00s -> 4287.00s]  as the number of parameters.
[4287.00s -> 4290.00s]  And the number of optimizer states,
[4290.00s -> 4294.00s]  and for Adagrad, it's, you'll remember
[4294.00s -> 4300.00s]  we had to store the gradient squared.
[4300.00s -> 4302.00s]  So that's another copy of the parameters.
[4302.00s -> 4308.00s]  So putting it all together, we have the total memory
[4308.00s -> 4313.00s]  is assuming, you know, FP32, which means four bytes
[4313.00s -> 4317.00s]  times the number of parameters, number of activations,
[4317.00s -> 4320.00s]  number of gradients, and number of optimizer states.
[4320.00s -> 4324.00s]  Okay, and that gives us, you know, some number
[4324.00s -> 4329.00s]  which is 496 here.
[4330.00s -> 4333.00s]  Okay, so this is a fairly simple calculation.
[4333.00s -> 4336.00s]  In the assignment one, you're going to do this
[4336.00s -> 4339.00s]  for the transformer, which is a little bit more involved
[4339.00s -> 4342.00s]  because you have to, there's not just matrix multiplications
[4342.00s -> 4345.00s]  but there's many matrices, there's a tension,
[4345.00s -> 4347.00s]  and there's all these other things.
[4347.00s -> 4351.00s]  But the general form of the calculation is the same.
[4351.00s -> 4354.00s]  You have parameters, activations, gradients,
[4354.00s -> 4358.00s]  and optimizer states.
[4359.00s -> 4367.00s]  Okay, and the, so, and the flops required, again,
[4367.00s -> 4372.00s]  for this model is six times the number of tokens
[4372.00s -> 4375.00s]  or number of data points times the number of parameters.
[4375.00s -> 4379.00s]  And, you know, that's basically concludes
[4379.00s -> 4383.00s]  the resource accounting for this particular model.
[4383.00s -> 4387.00s]  And if, for reference, if you're curious
[4387.00s -> 4390.00s]  about working this out for transformers,
[4390.00s -> 4394.00s]  you can consult some of these articles.
[4394.00s -> 4399.00s]  Okay, so in the remaining time, I think,
[4399.00s -> 4402.00s]  maybe I'll pause for questions.
[4402.00s -> 4404.00s]  We talked about building up the tensors
[4404.00s -> 4407.00s]  and then we built a kind of a very small model
[4407.00s -> 4411.00s]  and, you know, we talked about optimization
[4411.00s -> 4413.00s]  and how many, how much memory
[4413.00s -> 4416.00s]  and how much compute was required.
[4419.00s -> 4420.00s]  Yeah.
[4420.00s -> 4425.00s]  So the question is why do you need to store the activations?
[4425.00s -> 4428.00s]  So naively you need to store the activations
[4428.00s -> 4433.00s]  because when you're, when you're doing the p-core pass,
[4433.00s -> 4436.00s]  the gradients of, let's say the first layer
[4436.00s -> 4437.00s]  depend on the activation.
[4437.00s -> 4438.00s]  So the gradients of the i-th layer
[4438.00s -> 4441.00s]  depends on the activation there.
[4441.00s -> 4443.00s]  Now if you're smarter,
[4443.00s -> 4446.00s]  you don't have to store the activations
[4446.00s -> 4447.00s]  or you don't have to store all of them.
[4447.00s -> 4449.00s]  You can recompute them
[4449.00s -> 4451.00s]  and that's something our technique
[4451.00s -> 4453.00s]  will call activation checkpointing
[4453.00s -> 4456.00s]  which we can talk about later.
[4459.00s -> 4462.00s]  Okay, so let's just do this quick,
[4462.00s -> 4464.00s]  you know, actually there's not much to say here
[4464.00s -> 4466.00s]  but, you know, here's your typical,
[4466.00s -> 4468.00s]  you know, training loop
[4469.00s -> 4471.00s]  where you define the model,
[4471.00s -> 4473.00s]  define the optimizer
[4473.00s -> 4475.00s]  and you get the data
[4476.00s -> 4478.00s]  feed forward, backward
[4478.00s -> 4481.00s]  and take a step in a parameter space.
[4483.00s -> 4484.00s]  And
[4486.00s -> 4487.00s]  I guess
[4489.00s -> 4490.00s]  it'd be more interesting,
[4490.00s -> 4491.00s]  I guess next time I should show
[4491.00s -> 4493.00s]  like an actual 1D plot
[4493.00s -> 4496.00s]  which isn't available on this version.
[4499.00s -> 4500.00s]  So
[4501.00s -> 4503.00s]  one note about checkpointing.
[4505.00s -> 4508.00s]  So training language models takes a long time
[4508.00s -> 4511.00s]  and you're certainly will crash at some point
[4511.00s -> 4513.00s]  so you don't want to lose all your progress.
[4513.00s -> 4516.00s]  So you want to periodically save your model to disk
[4516.00s -> 4518.00s]  and just to be very clear,
[4518.00s -> 4520.00s]  the thing you want to save is
[4520.00s -> 4522.00s]  both the model
[4522.00s -> 4524.00s]  and the optimizer
[4525.00s -> 4527.00s]  and probably which iteration you're on,
[4527.00s -> 4528.00s]  I should add that
[4528.00s -> 4531.00s]  and then you can just load it up.
[4533.00s -> 4535.00s]  One maybe final note
[4535.00s -> 4536.00s]  and is
[4537.00s -> 4541.00s]  I alluded to kind of mixed precision training.
[4543.00s -> 4546.00s]  Choice of the data type has different trade-offs.
[4546.00s -> 4548.00s]  If you have higher precision
[4548.00s -> 4551.00s]  it's more accurate and stable
[4551.00s -> 4553.00s]  but it's more expensive
[4553.00s -> 4556.00s]  and lower precision is vice versa.
[4556.00s -> 4557.00s]  And
[4557.00s -> 4559.00s]  as we mentioned before
[4559.00s -> 4563.00s]  by default the recommendations use flow 32
[4563.00s -> 4567.00s]  but try to use BF16 or even FP8 whenever possible.
[4568.00s -> 4572.00s]  So you can use lower precision for the feed forward pass
[4572.00s -> 4575.00s]  but flow 32 for the rest.
[4575.00s -> 4579.00s]  And this is an idea that goes back to the 2017
[4579.00s -> 4582.00s]  when there's exploring mixed precision training.
[4582.00s -> 4585.00s]  PyTorch has some tools that automatically allow you
[4585.00s -> 4588.00s]  to do mixed precision training
[4589.00s -> 4591.00s]  because it can be sort of annoying to
[4591.00s -> 4594.00s]  have to specify which parts of your model
[4594.00s -> 4597.00s]  it needs to be what precision.
[4597.00s -> 4600.00s]  Generally you define your model as
[4600.00s -> 4602.00s]  sort of this clean modular thing
[4602.00s -> 4606.00s]  and specifying the precision is sort of like
[4606.00s -> 4610.00s]  something that needs to cut across that.
[4611.00s -> 4612.00s]  And
[4613.00s -> 4615.00s]  I guess maybe one kind of general comment is that
[4615.00s -> 4620.00s]  people are pushing the envelope on what precision is needed.
[4620.00s -> 4624.00s]  There's some papers that show you can actually use
[4624.00s -> 4627.00s]  FP8 all the way through.
[4630.00s -> 4632.00s]  I guess one of the challenges is
[4632.00s -> 4634.00s]  of course when you have lower precision
[4634.00s -> 4636.00s]  it gets very numerically unstable
[4636.00s -> 4639.00s]  but then you can do various tricks to
[4639.00s -> 4643.00s]  control the numerics of your model during training
[4643.00s -> 4646.00s]  so that you don't get into these bad regimes.
[4646.00s -> 4649.00s]  So this is where I think
[4649.00s -> 4652.00s]  the systems and the model architecture design
[4652.00s -> 4654.00s]  kind of are synergistic
[4654.00s -> 4659.00s]  because you want to design models now that we have
[4659.00s -> 4662.00s]  a lot of model design is just governed by hardware.
[4662.00s -> 4665.00s]  So even the transformer as we mentioned last time
[4665.00s -> 4667.00s]  is governed by having GPUs
[4667.00s -> 4669.00s]  and now if we notice that
[4669.00s -> 4672.00s]  Nvidia chips have the property that
[4672.00s -> 4676.00s]  if lower precision, even like int four
[4676.00s -> 4678.00s]  for example is one thing,
[4678.00s -> 4681.00s]  now if you can make your model training
[4681.00s -> 4684.00s]  actually work on int four which is I think
[4684.00s -> 4687.00s]  quite hard then you can get massive
[4687.00s -> 4691.00s]  speed ups and your model will be more efficient.
[4692.00s -> 4697.00s]  Now there's another thing which we'll talk about later
[4697.00s -> 4699.00s]  which is often you'll train your model
[4699.00s -> 4702.00s]  using more sane floating point
[4702.00s -> 4704.00s]  but when it comes to inference
[4704.00s -> 4707.00s]  you can go crazy and you take your model
[4707.00s -> 4709.00s]  and then you can quantize it and
[4709.00s -> 4712.00s]  get a lot of the gains from very very
[4712.00s -> 4714.00s]  aggressive quantization.
[4714.00s -> 4716.00s]  So somehow training is a lot
[4716.00s -> 4718.00s]  more difficult to do with low precision
[4718.00s -> 4720.00s]  but once you have a trained model
[4720.00s -> 4724.00s]  it's much easier to make it low precision.
[4724.00s -> 4729.00s]  Okay, so I will wrap up there just to conclude.
[4729.00s -> 4733.00s]  We have talked about the different primitives
[4733.00s -> 4735.00s]  to use to train a model building up from tensors
[4735.00s -> 4737.00s]  all the way to the training loop.
[4737.00s -> 4741.00s]  We talked about memory accounting and flops accounting
[4741.00s -> 4743.00s]  for these simple models.
[4743.00s -> 4746.00s]  Hopefully once you go through assignment one
[4746.00s -> 4748.00s]  all of these concepts will be really solid
[4748.00s -> 4751.00s]  because you'll be applying these ideas
[4751.00s -> 4754.00s]  for the actual transformer.
[4754.00s -> 4756.00s]  Okay, see you next time.
