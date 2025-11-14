This is a chat client that provides finantial information on a niche subset of organizations: all Mexican organizations that reported a form 6-K to the Securities Exchange Commission ("SEC") during the last four (4) years. The companies are contained in the following table:

              Name	                                                                        Exchange	Ticker	    Currency
        CEMEX, S.A.B. de C.V.	                                                                  XNYS	    CX	      USD
        CEMEX, S.A.B. de C.V.	                                                                  XMEX	    CEMEXCPO 	MXN
        Grupo Aeroportuario del Centro Norte S.A.B. de C.V. ADS (American Depositary Shares)	  XNAS	    OMAB	    USD
        Grupo Aeroportuario del Centro Norte S.A.B. de C.V.	                                    OTCPK	    GAERF	    USD
        Grupo Aeroportuario del Centro Norte S.A.B. de C.V.	                                    XMEX	    OMA	      MXN
        Grupo Aeroportuario del Pacífico, S.A.B. de C.V. ADR (American Depositary Receipt)	    XNYS	    PAC	      USD
        Grupo Aeroportuario del Pacífico, S.A.B. de C.V.	                                      OTCPK	    GPAEF	    USD
        Grupo Aeroportuario del Pacífico, S.A.B. de C.V.	                                      XMEX	    GAPB	    MXN
        Vista Energy S.A.B. de C.V. ADR (American Depositary Receipt)	                          XNYS	    VIST	    USD
        Vista Energy S.A.B. de C.V. ADR (American Depositary Receipt)	                          XMEX	    VISTAA	  MXN
        America Movil SAB de CV ADR - Series B	                                                XNYS	    AMX	      USD
        America Movil SAB de CV	X                                                               MEX	      AMXB	    MXN
        Corporación Inmobiliaria Vesta, S.A.B. de C.V.	                                        XNYS	    VTMX	    USD
        Corporación Inmobiliaria Vesta, S.A.B. de C.V. 	                                        XMEX	    VESTA	    MXN
        Grupo Financiero Santander Mexico SAB De CV Series B ADR (American Depositary Receipt)	XNYS	    BSMX	    USD
        Grupo Financiero Santander Mexico SAB De CV	                                            XMEX	    BSMXB	    MXN
        Petróleos Mexicanos (Pemex) - Bonds	                                                    XFRA		
        Grupo TMM SAB	                                                                          XMEX	    TMMA	    MXN
        Grupo TMM SAB	                                                                          OTCPK	    TMAY	    USD
        Betterware de Mexico SAPI de CV	                                                        XNYS	    BWMX	    USD

Non-US companies listed in US exchanges have some reporting obligations to the Securities Exchange Commission ("SEC").
Nowadays, the Electronic Data Gathering, Analysis, and Retrieval (EDGAR) system handles filings and queries.
6-k is a specific form that the non-US companies listed in US exchanges must submit.
The companies in the table are the only companies incorporated in Mexico that did submit the form 6-K anytime during the last 4 years.

The companies that do not appear both the USD and MXN counterpart, the counterpart might exist, I did not find it. 
Also, Pemex is not a private company, it is an organization owned by the Mexican Government. As such, you cannot buy shares, you can buy bonds. I did not find it listed in US exchanges, it is lited in European exchanges, but still is reporting 6-K form to SEC, I did not dig into the details.

This chat client is an agent. Along with the query, it sends some tools. One of the tools is a RAG on a set of 1010 documents from EDGAR database.

### RAG - How did I obtain the embeddings

First step was to download the documents from EDGAR. EDGAR has few API's, which are not that intuitive. There are some commercial API's and some python packages meant to make it easier. I preferred to connect directly to EDGAR API myself. First, I did the search in the website, found that since 2001 there were 30 organizations and about 5000 documents. I copied the name of the companies along with an id, the Central Index Key (CIK). In an Excel, I created a clean list of the 30 CIK. With some code, I connected to the API and downloaded 5000 html documents. Due to size concerns, I repeated the process, now I compromised on the last 4 years, 10 organizations and 1010 html documents.  

Then, I tried few methods to upload the html into memory. Avoided Unstructured, started with BSHTMLLoader, which strips the html tags and returns only the text. Because there are tables with values, I thought I needed to try something else. I tried reading the file directly and getting all tags and text. Still, it looked like the html tags were going to confuse the model when embedding. I ended up reading them directly, then parsing them with BeautifulSoup and adding markdowns to help the model read the tables. Spoiler: this did not work, but I did not know until the end.

Once all html in memory, I used RecursiveCharacterTextSplitter, chunk_size 1000, overlap 200, split about 1000 filings into about 63,500 chunks. In order to use the batch processing capacity of OpenAI(), I prepared the batches, jsonl, 1 id + 1 chunk -> 1 line, 10,000 chunks each, 7 batches. The first custom_id I created gave me error. My mistake, unique id for document and chunk starting character, but with the smart spliter algorythm, sometimes starts from a spot, decides a short chunk, later choses to start from same spot with a longer chunk: 2 chunks with same id in the same batch, error. Solved. I sent 4+3 to do not hit 50,000 lines limit in a batch process. Then 6 batches finished within the 24 hour window, not the 7th. Finally, I got them all, in 3 different batch processes. I downloaded them and stored them in a jsonl in my files. Then I loaded them to memory, created a persistent chromadb database, stored them in a collection in the database, in groups of 5000, below the limit of 5461, it used 17GB of RAM. 
I considered doing all this using LangChain document objects, through the whole workflow, including the embeddings. But it does not support batch processing them. Once I decided to get the embeddings in batch processing, it didn't make sense to convert back and forth, it was clearer manually in jsonl.

At this point, I could test it. With the first query I already knew there was something wrong. I used querions like:
"What was the revenue of Cemex in 2023?", "How much were the Mexican Government contributions in PETRÓLEOS MEXICANOS as of March 31, 2023?", "For BANCO SANTANDER MÉXICO, regarding Deposits, what was the December 2022 YoY increase?", "For BANCO SANTANDER MÉXICO, what was the gross operating income for 4Q22?". 
In could find the answers in the documents and see that the results retrieved did not answer the question. It look to me like the model was not able to understand the numbers and lines conforming a table as a table itself. Some of the answers were not in tables. It looked to me that things like Q2_2022 instead of Q4_2022 did not penalize much in the similarity distances. 
At this point, there was no time to do them all again. Some ideas that I would try if I will do it again are:
- Chunk size of 1000 is small, I would bring it to 2000. But I can tell that this is not the problem, it will not solve the issue.
- I would try a different embedding model, but still I think I shouldn't rely all on the model
- I would try to feed a big chunk with a table into a powerful model and ask him to verbalize the table, meaning, to generate text that would describe what is each value. With all these new paragraphs generated, I would try this model again.
By now, lets experiment with and enjoy what we have.