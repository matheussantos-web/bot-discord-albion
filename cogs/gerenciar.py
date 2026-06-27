import discord
from discord.ext import commands
from config import CANAL_DG
from cogs.content import conteudos_ativos, montar_embed


class GerenciarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, membro: discord.Member = None, *, classe: str = None):
        """Uso: !add @membro CLASSE"""
        if not membro or not classe:
            return await ctx.send('❌ Uso: `!add @membro CLASSE`', delete_after=5)

        view = next((v for v in conteudos_ativos.values() if v.criador_id == ctx.author.id), None)
        if not view:
            return await ctx.send('❌ Você não tem conteúdo ativo.', delete_after=5)

        classe = classe.upper()
        if classe not in view.membros:
            classes_disponiveis = ', '.join(view.membros.keys())
            return await ctx.send(f'❌ Classe inválida. Disponíveis: `{classes_disponiveis}`', delete_after=5)

        if view.vagas_usadas >= view.vagas:
            return await ctx.send('❌ Conteúdo lotado!', delete_after=5)

        if membro.id in view.inscritos:
            return await ctx.send(f'❌ {membro.display_name} já está nesse conteúdo.', delete_after=5)

        view.membros[classe].append(membro.id)
        view.inscritos[membro.id] = classe
        view.vagas_usadas += 1

        canal = discord.utils.get(ctx.guild.channels, name=CANAL_DG)
        msg = await canal.fetch_message(view.msg_id)
        await msg.edit(embed=montar_embed(
            view.titulo, view.tier, view.data, view.hora,
            view.criador_id, view.membros, view.vagas_usadas, view.vagas
        ))

        await ctx.send(f'✅ {membro.display_name} adicionado como **{classe}**.', delete_after=5)

    @commands.command()
    async def rem(self, ctx, membro: discord.Member = None):
        """Uso: !rem @membro"""
        if not membro:
            return await ctx.send('❌ Uso: `!rem @membro`', delete_after=5)

        view = next((v for v in conteudos_ativos.values() if v.criador_id == ctx.author.id), None)
        if not view:
            return await ctx.send('❌ Você não tem conteúdo ativo.', delete_after=5)

        if membro.id not in view.inscritos:
            return await ctx.send('❌ Membro não está nesse conteúdo.', delete_after=5)

        classe = view.inscritos.pop(membro.id)
        view.membros[classe].remove(membro.id)
        view.vagas_usadas -= 1

        canal = discord.utils.get(ctx.guild.channels, name=CANAL_DG)
        msg = await canal.fetch_message(view.msg_id)
        await msg.edit(embed=montar_embed(
            view.titulo, view.tier, view.data, view.hora,
            view.criador_id, view.membros, view.vagas_usadas, view.vagas
        ))

        await ctx.send(f'✅ {membro.display_name} removido do conteúdo.', delete_after=5)

    @commands.command()
    async def fechar(self, ctx):
        """Encerra o conteúdo ativo do criador"""
        view = next((v for v in conteudos_ativos.values() if v.criador_id == ctx.author.id), None)
        if not view:
            return await ctx.send('❌ Você não tem conteúdo ativo.', delete_after=5)

        canal = discord.utils.get(ctx.guild.channels, name=CANAL_DG)
        try:
            msg = await canal.fetch_message(view.msg_id)
            await msg.delete()
        except:
            pass

        conteudos_ativos.pop(view.msg_id, None)
        await ctx.send('✅ Conteúdo encerrado!', delete_after=5)


async def setup(bot):
    await bot.add_cog(GerenciarCog(bot))