import discord
from utils import send_request

class GroupMeet:

    def __init__(self,client,channel_id):
        self.channel_id = channel_id#os.environ['GBU_CHANNEL']
        self.client = client
        self.is_active = False
        self.reaction_message = None
        self.accepted_user_list = []
        self.rejected_user_list = []
        self.accepted_username_list = []
        self.rejected_username_list = []
        self.reactions = ["👍", "👎"]
        self.description = "Are you interested in this week's group meet?"
        self.prompt = self._get_basic_prompt()
        self._add_reaction_fields()

    def _get_basic_prompt(self):
        return discord.Embed(title='Group Meet ', 
                                description=self.description).set_thumbnail(url='https://community.pepperdine.edu/it/images/googlemeetsmall.jpg')


    def _add_reaction_fields(self):
        self.prompt.add_field(name="To accept the invite react with ",value="👍",inline=False)
        self.prompt.add_field(name="To reject the invite react with ",value="👎",inline=False)
    
    async def _add_reactions(self):
        for reaction in self.reactions:
            await self.reaction_message.add_reaction(reaction)
    
    async def send_message(self):
      self.reaction_message = await self.client.get_channel(int(self.channel_id)).send(embed=self.prompt)
      await self._add_reactions()
      self.is_active = True
        
    async def on_reaction(self,payload):
      if self.is_active and payload.message_id == self.reaction_message.id and payload.member.bot==False:
        # print(payload)
        if payload.emoji.name=="👍":
          print("added")
          await self.add_users_to_db(payload.user_id,choice=1)
          if payload.user_id not in self.accepted_user_list:
            self.accepted_user_list.append(payload.user_id)
            self.accepted_username_list.append(payload.member.name)
          try:
            self.rejected_user_list.remove(payload.user_id)
            self.rejected_username_list.remove(payload.member.name)
          except:
            pass

        elif payload.emoji.name=="👎":
          print("removed")
          await self.add_users_to_db(payload.user_id,choice=0)
          if payload.user_id not in self.rejected_user_list:
            self.rejected_user_list.append(payload.user_id)
            self.rejected_username_list.append(payload.member.name)
          try:
            self.accepted_user_list.remove(payload.user_id)
            self.accepted_username_list.remove(payload.member.name)
          except:
            pass
          
        self.prompt = self._get_basic_prompt()
        self.prompt.add_field(name="To accept the invite react with 👍",value="Accepted User List\n"+"\n".join(self.accepted_username_list),inline=False)
        self.prompt.add_field(name="To reject the invite react with 👎",value="Rejected User List\n"+"\n".join(self.rejected_username_list),inline=False)
        await self.reaction_message.clear_reactions()
        await self._add_reactions()
        await self.reaction_message.edit(embed=self.prompt)
        
    async def add_users_to_db(self,user_id,choice):
      headers = {'Content-Type': 'application/json'}
      payload = '{\n"data":{"attributes": {\n"discord_id": '+str(user_id)+',\n "choice\":'+str(choice)+'\n}\n}\n}'
      await send_request(method_type="POST",url="groupcalls/",headers=headers,data=payload)

      
    
    async def post_groups_to_channel(self):
      headers = {'Content-Type': 'application/json'}

      groups_list = await send_request(method_type="GET",url="groupcalls/",headers=headers).json()
      
      groups={}
      for data in groups_list:
        user_id,idx = data
        if idx not in groups:
          groups[idx]=[]
        groups[idx].append(user_id)

    
      getMentionStr = lambda x: f"<@{str(x)}>"
      getAssignedGroupPromptDescription = lambda grp: f"**Group Lead**: {getMentionStr(grp[0])}\n"+"**Members**: "+ " ".join(list(map(getMentionStr,grp)))
  
      prompt = discord.Embed(title='Assigned Groups', 
                                description="Pls, find your respected groups for this week's Group Meeting").set_thumbnail(url='https://lh3.googleusercontent.com/proxy/FvYtnlrHTrrcmQiZuvp3lLqyODoJdEzi2-j_TBUVssLXgzaLRHmFQ8ZvxDSIvT3brHbU4qA0NBC2hW7zCnjNiG5BlAaLhJKtBJpeWdHZmKM')
      for idx,grp in enumerate(groups.values()):
        prompt.add_field(name=f"-------------------'Group-{str(idx+1).zfill(2)}'-------------------",value=getAssignedGroupPromptDescription(grp),inline=False)
        
      await self.client.get_channel(int(self.channel_id)).send(embed=prompt)

          
    