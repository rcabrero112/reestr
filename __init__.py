from .reestr import WebhookHandlerCog


def setup(bot):
    bot.add_cog(WebhookHandlerCog(bot))