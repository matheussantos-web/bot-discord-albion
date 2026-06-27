import discord
from discord.ext import commands
from discord.ui import View, Button
from config import CANAL_DG, GUILD_NOME

conteudos_ativos = {}


def montar_embed(titulo, tier, data, hora, lider_id, membros, fila, vagas_usadas, vagas):
    vagas_restantes = vagas - vagas_usadas
    status = '🔴 LOTADO' if vagas_restantes == 0 else f'🟢 {vagas_restantes} vagas restantes'

    lista = ''
    for classe, inscritos in membros.items():
        if inscritos:
            mencoes = ', '.join(f'<@{uid}>' for uid in inscritos)
            lista += f'**{classe}** — {mencoes}'
        else:
            lista += f'**{classe}** — vaga aberta'

        # Mostra fila se houver
        if fila.get(classe):
            fila_mencoes = ', '.join(f'<@{uid}>' for uid in fila[classe])
            lista += f' *(fila: {fila_mencoes})*'

        lista += '\n'

    data_texto = f'{data} às {hora}' if hora else data

    embed = discord.Embed(
        title=f'⚔️ {titulo.upper()} — {tier}',
        description=(
            f'📅 **Data:** {data_texto}\n'
            f'👤 **Caller:** <@{lider_id}>\n'
            f'👥 **Vagas:** {vagas_usadas}/{vagas} — {status}\n\n'
            f'📋 **Classes:**\n{lista}'
        ),
        color=0xFF4444
    )
    embed.set_footer(text=f'Selecione sua função abaixo • {GUILD_NOME}')
    return embed


class ContentView(View):
    def __init__(self, msg_id, criador_id, canal, membros, vagas, titulo, tier, data, hora):
        super().__init__(timeout=None)
        self.msg_id = msg_id
        self.criador_id = criador_id
        self.canal = canal
        self.membros = membros
        self.vagas = vagas
        self.vagas_usadas = 0
        self.inscritos = {}   # {user_id: classe}
        self.fila = {}        # {classe: [user_id, ...]}
        self.titulo = titulo
        self.tier = tier
        self.data = data
        self.hora = hora

        for classe in membros.keys():
            btn = Button(label=classe, style=discord.ButtonStyle.blurple)
            btn.callback = self.fazer_callback(classe)
            self.add_item(btn)

        sair_btn = Button(label='🚪 Sair', style=discord.ButtonStyle.danger, row=4)
        sair_btn.callback = self.sair
        self.add_item(sair_btn)

        fechar_btn = Button(label='🔒 Fechar', style=discord.ButtonStyle.gray, row=4)
        fechar_btn.callback = self.fechar
        self.add_item(fechar_btn)

    def fazer_callback(self, classe):
        async def callback(interaction: discord.Interaction):
            user_id = interaction.user.id

            # Já tá nessa classe
            if self.inscritos.get(user_id) == classe:
                return await interaction.response.send_message(
                    f'❌ Você já está como **{classe}**.', ephemeral=True
                )

            # Já tá na fila dessa classe
            if user_id in self.fila.get(classe, []):
                pos = self.fila[classe].index(user_id) + 1
                return await interaction.response.send_message(
                    f'❌ Você já está na fila de **{classe}** (posição {pos}).', ephemeral=True
                )

            # Sai da classe/fila antiga se tiver
            if user_id in self.inscritos:
                classe_antiga = self.inscritos.pop(user_id)
                self.membros[classe_antiga].remove(user_id)
                self.vagas_usadas -= 1

                # Promove próximo da fila da classe antiga
                if self.fila.get(classe_antiga):
                    proximo_id = self.fila[classe_antiga].pop(0)
                    self.membros[classe_antiga].append(proximo_id)
                    self.inscritos[proximo_id] = classe_antiga
                    self.vagas_usadas += 1
                    await interaction.channel.send(
                        f'<@{proximo_id}> você saiu da fila e entrou como **{classe_antiga}**! ✅',
                        delete_after=30
                    )
            else:
                # Remove da fila de outra classe se tiver
                for c, fila in self.fila.items():
                    if user_id in fila:
                        fila.remove(user_id)
                        break

            # Classe já tem alguém — vai pra fila
            if len(self.membros[classe]) >= 1:
                self.fila.setdefault(classe, []).append(user_id)
                pos = len(self.fila[classe])
                await interaction.response.send_message(
                    f'⏳ **{classe}** já está ocupado. Você entrou na fila! (posição {pos})',
                    ephemeral=True
                )
            else:
                # Vaga livre
                if self.vagas_usadas >= self.vagas:
                    return await interaction.response.send_message('❌ Conteúdo lotado!', ephemeral=True)

                self.membros[classe].append(user_id)
                self.inscritos[user_id] = classe
                self.vagas_usadas += 1

                await interaction.response.send_message(
                    f'✅ Você entrou como **{classe}**!', ephemeral=True
                )

            msg = await self.canal.fetch_message(self.msg_id)
            await msg.edit(embed=montar_embed(
                self.titulo, self.tier, self.data, self.hora,
                self.criador_id, self.membros, self.fila, self.vagas_usadas, self.vagas
            ))
        return callback

    async def sair(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # Sai da fila se tiver em alguma
        for classe, fila in self.fila.items():
            if user_id in fila:
                fila.remove(user_id)
                await interaction.response.send_message(
                    f'✅ Você saiu da fila de **{classe}**.', ephemeral=True
                )
                msg = await self.canal.fetch_message(self.msg_id)
                await msg.edit(embed=montar_embed(
                    self.titulo, self.tier, self.data, self.hora,
                    self.criador_id, self.membros, self.fila, self.vagas_usadas, self.vagas
                ))
                return

        if user_id not in self.inscritos:
            return await interaction.response.send_message('❌ Você não está nesse conteúdo.', ephemeral=True)

        classe = self.inscritos.pop(user_id)
        self.membros[classe].remove(user_id)
        self.vagas_usadas -= 1

        # Promove próximo da fila
        proximo = None
        if self.fila.get(classe):
            proximo_id = self.fila[classe].pop(0)
            self.membros[classe].append(proximo_id)
            self.inscritos[proximo_id] = classe
            self.vagas_usadas += 1
            proximo = proximo_id

        await interaction.response.send_message('✅ Você saiu do conteúdo.', ephemeral=True)

        if proximo:
            await interaction.channel.send(
                f'<@{proximo}> você saiu da fila e entrou como **{classe}**! ✅',
                delete_after=30
            )

        msg = await self.canal.fetch_message(self.msg_id)
        await msg.edit(embed=montar_embed(
            self.titulo, self.tier, self.data, self.hora,
            self.criador_id, self.membros, self.fila, self.vagas_usadas, self.vagas
        ))

    async def fechar(self, interaction: discord.Interaction):
        if interaction.user.id != self.criador_id:
            return await interaction.response.send_message('❌ Só o criador pode fechar.', ephemeral=True)

        conteudos_ativos.pop(self.msg_id, None)
        await interaction.message.delete()
        await interaction.response.send_message('✅ Conteúdo encerrado!', ephemeral=True)


class ContentCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def content(self, ctx, *, args: str = None):
        """
        Com data/hora: !content DG AVA / 8.4 / 25/06 / 14:00 / TANK HEAL SILENCE
        Sem data/hora: !content DG AVA / 8.4 / TANK HEAL SILENCE
        """

        if not args:
            return await ctx.send(
                '❌ Uso:\n'
                'Com data: `!content titulo / tier / data / hora / CLASSE1 CLASSE2 ...`\n'
                'Sem data: `!content titulo / tier / CLASSE1 CLASSE2 ...`',
                delete_after=10
            )

        partes = [p.strip() for p in args.split(' / ')]

        if len(partes) < 3:
            return await ctx.send(
                '❌ Faltam parâmetros! Separa com ` / `\n'
                'Com data: `!content DG AVA / 8.4 / 25/06 / 14:00 / TANK HEAL`\n'
                'Sem data: `!content DG AVA / 8.4 / TANK HEAL`',
                delete_after=10
            )

        titulo = partes[0]
        tier   = partes[1]

        tem_data = len(partes) >= 5 and (':' in partes[3] or '/' in partes[2])

        if tem_data:
            data    = partes[2]
            hora    = partes[3]
            classes = partes[4].split()
        else:
            data    = '🟢 Agora'
            hora    = ''
            classes = partes[2].split()

        if not classes:
            return await ctx.send('❌ Coloca pelo menos uma classe!', delete_after=5)

        canal = discord.utils.get(ctx.guild.channels, name=CANAL_DG)
        if not canal:
            return await ctx.send(f'❌ Canal `#{CANAL_DG}` não encontrado.', delete_after=5)

        vagas    = len(classes)
        membros  = {classe.upper(): [] for classe in classes}
        lider_id = ctx.author.id

        await ctx.message.delete()

        msg = await canal.send('@here', embed=montar_embed(titulo, tier, data, hora, lider_id, membros, {}, 0, vagas))

        view = ContentView(
            msg_id=msg.id, criador_id=ctx.author.id, canal=canal,
            membros=membros, vagas=vagas, titulo=titulo,
            tier=tier, data=data, hora=hora
        )

        conteudos_ativos[msg.id] = view
        await msg.edit(view=view)

        if canal != ctx.channel:
            await ctx.send(f'✅ Conteúdo criado em {canal.mention}!', delete_after=5)


async def setup(bot):
    await bot.add_cog(ContentCog(bot))