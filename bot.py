import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import yt_dlp

TOKEN = TOKEN_ICI


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ─── ÉCONOMIE ─────────────────────────────────────────────
economie = {}

def get_solde(user_id):
    if user_id not in economie:
        economie[user_id] = 0
    return economie[user_id]

# ─── DÉMARRAGE ────────────────────────────────────────────
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ {bot.user} est en ligne !")

# ─── BIENVENUE + RÔLE AUTO ────────────────────────────────
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="bienvenue")
    if channel:
        embed = discord.Embed(
            title=f"👋 Bienvenue sur {member.guild.name} !",
            description=f"Heureux de t'accueillir {member.mention} !\nLis bien le règlement et bonne session RP ! 🎮",
            color=0x3498db
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)
    role = discord.utils.get(member.guild.roles, name="Citoyen")
    if role:
        await member.add_roles(role)

# ─── LOGS ─────────────────────────────────────────────────
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="logs")
    if channel:
        await channel.send(f"📤 **{member.name}** a quitté le serveur.")

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    channel = discord.utils.get(message.guild.text_channels, name="logs")
    if channel:
        await channel.send(f"🗑️ Message de **{message.author.name}** supprimé dans {message.channel.mention} :\n> {message.content}")

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    if before.content == after.content:
        return
    channel = discord.utils.get(before.guild.text_channels, name="logs")
    if channel:
        await channel.send(f"✏️ Message de **{before.author.name}** modifié dans {before.channel.mention} :\n> Avant : {before.content}\n> Après : {after.content}")

@bot.event
async def on_member_ban(guild, user):
    channel = discord.utils.get(guild.text_channels, name="logs")
    if channel:
        await channel.send(f"🔨 **{user.name}** a été banni du serveur.")

@bot.event
async def on_member_unban(guild, user):
    channel = discord.utils.get(guild.text_channels, name="logs")
    if channel:
        await channel.send(f"✅ **{user.name}** a été débanni du serveur.")

# ─── MODÉRATION ───────────────────────────────────────────
@bot.tree.command(name="kick", description="Expulser un membre")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison"):
    await membre.kick(reason=raison)
    await interaction.response.send_message(f"👢 {membre.mention} a été expulsé. Raison : {raison}")
    logs = discord.utils.get(interaction.guild.text_channels, name="logs")
    if logs:
        await logs.send(f"👢 {membre.mention} expulsé par {interaction.user.mention}. Raison : {raison}")

@bot.tree.command(name="ban", description="Bannir un membre")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison"):
    await membre.ban(reason=raison)
    await interaction.response.send_message(f"🔨 {membre.mention} a été banni. Raison : {raison}")
    logs = discord.utils.get(interaction.guild.text_channels, name="logs")
    if logs:
        await logs.send(f"🔨 {membre.mention} banni par {interaction.user.mention}. Raison : {raison}")

@bot.tree.command(name="clear", description="Supprimer des messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, nombre: int):
    await interaction.channel.purge(limit=nombre)
    await interaction.response.send_message(f"🗑️ {nombre} messages supprimés !", ephemeral=True)

@bot.tree.command(name="warn", description="Avertir un membre")
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, membre: discord.Member, raison: str):
    await interaction.response.send_message(f"⚠️ {membre.mention} a reçu un avertissement. Raison : {raison}")
    logs = discord.utils.get(interaction.guild.text_channels, name="logs")
    if logs:
        await logs.send(f"⚠️ {membre.mention} averti par {interaction.user.mention}. Raison : {raison}")

# ─── FICHE RP ─────────────────────────────────────────────
fiches = {}

@bot.tree.command(name="fiche", description="Créer ta fiche personnage RP")
async def fiche(interaction: discord.Interaction, nom: str, age: int, metier: str, bio: str):
    fiches[interaction.user.id] = {"nom": nom, "age": age, "metier": metier, "bio": bio}
    embed = discord.Embed(title="🪪 Fiche Personnage", color=0x3498db)
    embed.add_field(name="Nom", value=nom, inline=True)
    embed.add_field(name="Âge", value=age, inline=True)
    embed.add_field(name="Métier", value=metier, inline=True)
    embed.add_field(name="Biographie", value=bio, inline=False)
    embed.set_footer(text=f"Joueur : {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="voirfiche", description="Voir la fiche d'un joueur")
async def voirfiche(interaction: discord.Interaction, membre: discord.Member):
    if membre.id in fiches:
        f = fiches[membre.id]
        embed = discord.Embed(title=f"🪪 Fiche de {f['nom']}", color=0x3498db)
        embed.add_field(name="Âge", value=f["age"], inline=True)
        embed.add_field(name="Métier", value=f["metier"], inline=True)
        embed.add_field(name="Biographie", value=f["bio"], inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Ce joueur n'a pas de fiche RP.", ephemeral=True)

# ─── COMMANDES RP ─────────────────────────────────────────
@bot.tree.command(name="me", description="Action RP")
async def me(interaction: discord.Interaction, action: str):
    await interaction.response.send_message(f"*{interaction.user.display_name} {action}*")

@bot.tree.command(name="do", description="Description RP de la scène")
async def do(interaction: discord.Interaction, description: str):
    await interaction.response.send_message(f"📍 *{description}*")

@bot.tree.command(name="infraction", description="Signaler une infraction RP")
async def infraction(interaction: discord.Interaction, suspect: discord.Member, motif: str):
    embed = discord.Embed(title="🚨 Rapport d'infraction", color=0xe74c3c)
    embed.add_field(name="Suspect", value=suspect.mention, inline=True)
    embed.add_field(name="Rapporté par", value=interaction.user.mention, inline=True)
    embed.add_field(name="Motif", value=motif, inline=False)
    await interaction.response.send_message(embed=embed)

# ─── COMMANDES DOUANES ────────────────────────────────────
@bot.tree.command(name="fouille", description="Fouiller un véhicule ou un individu")
async def fouille(interaction: discord.Interaction, cible: discord.Member, resultat: str):
    embed = discord.Embed(title="🔍 Rapport de Fouille", color=0xf39c12)
    embed.add_field(name="Agent", value=interaction.user.mention, inline=True)
    embed.add_field(name="Cible", value=cible.mention, inline=True)
    embed.add_field(name="Résultat", value=resultat, inline=False)
    embed.set_footer(text="Service des Douanes")
    await interaction.response.send_message(embed=embed)
    logs = discord.utils.get(interaction.guild.text_channels, name="logs")
    if logs:
        await logs.send(f"🔍 Fouille de {cible.mention} par {interaction.user.mention} : {resultat}")

@bot.tree.command(name="controle", description="Effectuer un contrôle douanier")
async def controle(interaction: discord.Interaction, cible: discord.Member, plaque: str, statut: str):
    embed = discord.Embed(title="🛃 Contrôle Douanier", color=0x2ecc71)
    embed.add_field(name="Agent", value=interaction.user.mention, inline=True)
    embed.add_field(name="Conducteur", value=cible.mention, inline=True)
    embed.add_field(name="Plaque", value=plaque, inline=True)
    embed.add_field(name="Statut", value=statut, inline=False)
    embed.set_footer(text="Service des Douanes")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="verbalise", description="Verbaliser un individu")
async def verbalise(interaction: discord.Interaction, cible: discord.Member, motif: str, amende: int):
    economie[cible.id] = get_solde(cible.id) - amende
    embed = discord.Embed(title="📋 Procès-Verbal", color=0xe74c3c)
    embed.add_field(name="Agent", value=interaction.user.mention, inline=True)
    embed.add_field(name="Contrevenant", value=cible.mention, inline=True)
    embed.add_field(name="Motif", value=motif, inline=False)
    embed.add_field(name="Amende", value=f"{amende}$", inline=True)
    embed.add_field(name="Nouveau solde", value=f"{get_solde(cible.id)}$", inline=True)
    embed.set_footer(text="Service des Douanes")
    await interaction.response.send_message(embed=embed)
    logs = discord.utils.get(interaction.guild.text_channels, name="logs")
    if logs:
        await logs.send(f"📋 {cible.mention} verbalisé par {interaction.user.mention} : {motif} — {amende}$")

@bot.tree.command(name="saisie", description="Saisir des marchandises")
async def saisie(interaction: discord.Interaction, cible: discord.Member, marchandise: str, quantite: str):
    embed = discord.Embed(title="📦 Rapport de Saisie", color=0x9b59b6)
    embed.add_field(name="Agent", value=interaction.user.mention, inline=True)
    embed.add_field(name="Propriétaire", value=cible.mention, inline=True)
    embed.add_field(name="Marchandise", value=marchandise, inline=True)
    embed.add_field(name="Quantité", value=quantite, inline=True)
    embed.set_footer(text="Service des Douanes")
    await interaction.response.send_message(embed=embed)

# ─── ANNONCES ─────────────────────────────────────────────
@bot.tree.command(name="annonce", description="Faire une annonce officielle (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def annonce(interaction: discord.Interaction, titre: str, message: str, salon: discord.TextChannel):
    embed = discord.Embed(title=f"📢 {titre}", description=message, color=0xe74c3c)
    embed.set_footer(text=f"Annonce par {interaction.user.name}")
    await salon.send(embed=embed)
    await interaction.response.send_message(f"✅ Annonce envoyée dans {salon.mention} !", ephemeral=True)

@bot.tree.command(name="annoncerp", description="Faire une annonce RP (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def annoncerp(interaction: discord.Interaction, message: str, salon: discord.TextChannel):
    embed = discord.Embed(title="🎭 Annonce RP", description=message, color=0x3498db)
    embed.set_footer(text=f"Par {interaction.user.name}")
    await salon.send(embed=embed)
    await interaction.response.send_message(f"✅ Annonce RP envoyée dans {salon.mention} !", ephemeral=True)

# ─── ÉCONOMIE RP ──────────────────────────────────────────
@bot.tree.command(name="solde", description="Voir ton solde RP")
async def solde(interaction: discord.Interaction):
    s = get_solde(interaction.user.id)
    await interaction.response.send_message(f"💰 Ton solde : **{s}$**")

@bot.tree.command(name="payer", description="Payer un autre joueur")
async def payer(interaction: discord.Interaction, membre: discord.Member, montant: int):
    if montant <= 0:
        await interaction.response.send_message("❌ Le montant doit être positif.", ephemeral=True)
        return
    if get_solde(interaction.user.id) < montant:
        await interaction.response.send_message("❌ Tu n'as pas assez d'argent.", ephemeral=True)
        return
    economie[interaction.user.id] -= montant
    economie[membre.id] = get_solde(membre.id) + montant
    await interaction.response.send_message(f"💸 {interaction.user.mention} a payé **{montant}$** à {membre.mention}")

@bot.tree.command(name="donner", description="Donner de l'argent à un joueur (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def donner(interaction: discord.Interaction, membre: discord.Member, montant: int):
    economie[membre.id] = get_solde(membre.id) + montant
    await interaction.response.send_message(f"✅ **{montant}$** ajoutés au compte de {membre.mention}")

@bot.tree.command(name="retirer", description="Retirer de l'argent à un joueur (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def retirer(interaction: discord.Interaction, membre: discord.Member, montant: int):
    economie[membre.id] = get_solde(membre.id) - montant
    await interaction.response.send_message(f"✅ **{montant}$** retirés du compte de {membre.mention}")

# ─── MUSIQUE ──────────────────────────────────────────────
music_queue = []

@bot.tree.command(name="play", description="Jouer une musique depuis YouTube")
async def play(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Tu dois être dans un salon vocal !", ephemeral=True)
        return
    await interaction.response.defer()
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client is None:
        await channel.connect()
    ydl_opts = {"format": "bestaudio", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info["url"]
        titre = info.get("title", "Musique")
    source = discord.FFmpegPCMAudio(url2, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
    interaction.guild.voice_client.play(source)
    await interaction.followup.send(f"🎵 En cours de lecture : **{titre}**")

@bot.tree.command(name="stop", description="Arrêter la musique")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Musique arrêtée !")
    else:
        await interaction.response.send_message("❌ Aucune musique en cours.", ephemeral=True)

@bot.tree.command(name="pause", description="Mettre en pause la musique")
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("⏸️ Musique mise en pause !")
    else:
        await interaction.response.send_message("❌ Aucune musique en cours.", ephemeral=True)

@bot.tree.command(name="reprendre", description="Reprendre la musique")
async def reprendre(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("▶️ Musique reprise !")
    else:
        await interaction.response.send_message("❌ Aucune musique en pause.", ephemeral=True)

# ─── TICKETS ──────────────────────────────────────────────
# ─── TICKETS ──────────────────────────────────────────────

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💼 Projets & Entreprises", style=discord.ButtonStyle.primary, custom_id="ticket_projet", row=0)
    async def ticket_projet(self, interaction: discord.Interaction, button: discord.ui.Button):
        await creer_ticket(interaction, "projets-entreprises", "💼 Projets & Entreprises", "Décris ton projet ou ton entreprise RP.")

    @discord.ui.button(label="🔧 Problème Technique", style=discord.ButtonStyle.secondary, custom_id="ticket_technique", row=0)
    async def ticket_technique(self, interaction: discord.Interaction, button: discord.ui.Button):
        await creer_ticket(interaction, "probleme-technique", "🔧 Problème Technique", "Décris ton problème technique en détail.")

    @discord.ui.button(label="⚖️ Plainte Joueur", style=discord.ButtonStyle.danger, custom_id="ticket_plainte", row=1)
    async def ticket_plainte(self, interaction: discord.Interaction, button: discord.ui.Button):
        await creer_ticket(interaction, "plainte-joueur", "⚖️ Plainte Joueur", "Indique le pseudo du joueur et décris les faits.")

    @discord.ui.button(label="❓ Question", style=discord.ButtonStyle.success, custom_id="ticket_question", row=1)
    async def ticket_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        await creer_ticket(interaction, "question", "❓ Question", "Pose ta question, le staff te répondra dès que possible.")

async def creer_ticket(interaction: discord.Interaction, nom: str, titre: str, instructions: str):
    guild = interaction.guild
    
    # Vérifie si le joueur a déjà un ticket ouvert
    existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
    if existing:
        await interaction.response.send_message(f"❌ Tu as déjà un ticket ouvert : {existing.mention}", ephemeral=True)
        return

    # Crée le salon privé
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    
    # Donne accès au staff si le rôle existe
    staff_role = discord.utils.get(guild.roles, name="Staff")
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    channel = await guild.create_text_channel(
        name=f"ticket-{interaction.user.name.lower()}",
        overwrites=overwrites
    )

    # Message dans le ticket
    embed = discord.Embed(title=f"{titre}", color=0x00C9A7)
    embed.add_field(name="👤 Membre", value=interaction.user.mention, inline=True)
    embed.add_field(name="📁 Catégorie", value=titre, inline=True)
    embed.add_field(name="📝 Instructions", value=instructions, inline=False)
    embed.set_footer(text="Pour fermer ce ticket, tapez /fermerticket")
    
    await channel.send(embed=embed, view=FermerTicketView())
    await interaction.response.send_message(f"✅ Ton ticket a été créé : {channel.mention}", ephemeral=True)

    # Log
    logs = discord.utils.get(interaction.guild.text_channels, name="logs")
    if logs:
        await logs.send(f"🎫 Nouveau ticket **{titre}** ouvert par {interaction.user.mention} : {channel.mention}")

class FermerTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Fermer le ticket", style=discord.ButtonStyle.danger, custom_id="fermer_ticket")
    async def fermer_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket fermé. Ce salon sera supprimé dans 5 secondes.")
        logs = discord.utils.get(interaction.guild.text_channels, name="logs")
        if logs:
            await logs.send(f"🔒 Ticket {interaction.channel.mention} fermé par {interaction.user.mention}")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.tree.command(name="ticket", description="Envoyer le panel de tickets (admin)")
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Ouvrir un ticket",
        description="Clique sur le bouton correspondant à ta demande 👇",
        color=0x00C9A7
    )
    embed.add_field(name="💼 Projets & Entreprises", value="Créer ou gérer une entreprise RP", inline=True)
    embed.add_field(name="🔧 Problème Technique", value="Signaler un bug ou problème", inline=True)
    embed.add_field(name="⚖️ Plainte Joueur", value="Signaler un joueur", inline=True)
    embed.add_field(name="❓ Question", value="Poser une question au staff", inline=True)
    await interaction.response.send_message(embed=embed, view=TicketView())

@bot.tree.command(name="fermerticket", description="Fermer le ticket actuel")
async def fermerticket(interaction: discord.Interaction):
    if "ticket-" in interaction.channel.name:
        await interaction.response.send_message("🔒 Ticket fermé. Ce salon sera supprimé dans 5 secondes.")
        logs = discord.utils.get(interaction.guild.text_channels, name="logs")
        if logs:
            await logs.send(f"🔒 Ticket {interaction.channel.mention} fermé par {interaction.user.mention}")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("❌ Cette commande ne fonctionne que dans un ticket !", ephemeral=True)

bot.run(TOKEN)