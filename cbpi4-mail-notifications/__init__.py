
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
import cbpi
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationType
from cbpi.controller.notification_controller import NotificationController

import smtplib, ssl, email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



logger = logging.getLogger(__name__)

smtp_address = None
smtp_port = None
smtp_user = None
smtp_pass = None
smtp_encryption = None

class mail_notifications(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.run())


    async def run(self):
        plugin = await self.cbpi.plugin.load_plugin_list("cbpi4-mail-notifications")
        self.version=plugin[0].get("Version","0.0.0")
        self.name=plugin[0].get("Name","cbpi4-mail-notifications")

        self.mail_notifications_update = self.cbpi.config.get(self.name+"_update", None)

        logger.info('Starting Mail Notifications background task')
        await self.mail_notifications_settings()

        if smtp_address is None or smtp_address == "" or not smtp_address:
            logger.warning('Check SMTP Address is set')
        elif smtp_port is None or smtp_port == "" or not smtp_port:
            logger.warning('Check SMTP Port is set')
        elif smtp_user is None or smtp_user == "" or not smtp_user:
            logger.warning('Check SMTP Username is set')
        elif smtp_pass is None or smtp_pass == "" or not smtp_pass:
            logger.warning('Check SMTP Password is set')
        else:
            self.listener_ID = self.cbpi.notification.add_listener(self.messageEvent)
            logger.info("Mail Notifications Listener ID: {}".format(self.listener_ID))
        pass

    async def mail_notifications_settings(self):
        global smtp_address
        global smtp_port
        global smtp_user
        global smtp_pass
        global smtp_encryption

        smtp_address = self.cbpi.config.get("smtp_address", None)
        smtp_port = self.cbpi.config.get("smtp_port", None)
        smtp_user = self.cbpi.config.get("smtp_user", None)
        smtp_pass = self.cbpi.config.get("smtp_pass", None)
        smtp_encryption = self.cbpi.config.get("smtp_encryption", None)

        if smtp_address is None:
            logger.info("INIT SMTP Address")
            try:
                await self.cbpi.config.add("smtp_address", "", type=ConfigType.STRING, description="SMTP Address",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.mail_notifications_update == None or self.mail_notifications_update != self.version:
                try:
                    await self.cbpi.config.add("smtp_address", smtp_address, type=ConfigType.STRING, description="SMTP Address",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if smtp_port is None:
            logger.info("INIT SMTP Port")
            try:
                await self.cbpi.config.add("smtp_port", "", type=ConfigType.NUMBER, description="SMTP Port",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.mail_notifications_update == None or self.mail_notifications_update != self.version:
                try:
                    await self.cbpi.config.add("smtp_port", smtp_port, type=ConfigType.NUMBER, description="SMTP Port",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if self.mail_notifications_update == None or self.mail_notifications_update != self.version:
            try:
                await self.cbpi.config.add(self.name+"_update", self.version, type=ConfigType.STRING, description="Mail Notifications Update Version",source="hidden")
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)


        if smtp_user is None:
            logger.info("INIT SMTP User")
            try:
                await self.cbpi.config.add("smtp_user", "", type=ConfigType.STRING, description="SMTP Username",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.mail_notifications_update == None or self.mail_notifications_update != self.version:
                try:
                    await self.cbpi.config.add("smtp_user", smtp_user, type=ConfigType.STRING, description="SMTP Username",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if smtp_pass is None:
            logger.info("INIT SMTP Port")
            try:
                await self.cbpi.config.add("smtp_pass", "", type=ConfigType.STRING, description="SMTP Password",source=self.name)
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.mail_notifications_update == None or self.mail_notifications_update != self.version:
                try:
                    await self.cbpi.config.add("smtp_pass", smtp_pass, type=ConfigType.STRING, description="SMTP Password",source=self.name)
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)

        if smtp_encryption is None:
            logger.info("INIT SMTP Port")
            try:
                await self.cbpi.config.add("smtp_encryption", "TLS", type=ConfigType.SELECT, description="SMTP Encryption",source=self.name,
                                           options=[{"label":"TLS", "value":"TLS"},{"label":"SSL", "value":"SSL"},{"label":"Plain", "value":"Plain"}])
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)
        else:
            if self.mail_notifications_update == None or self.mail_notifications_update != self.version:
                try:
                    await self.cbpi.config.add("smtp_encryption", smtp_encryption, type=ConfigType.STRING, description="SMTP Encryption",source=self.name,
                                           options=[{"label":"TLS", "value":"TLS"},{"label":"SSL", "value":"SSL"},{"label":"Plain", "value":"Plain"}])
                except Exception as e:
                    logger.warning('Unable to update config')
                    logger.error(e)


        if self.mail_notifications_update == None or self.mail_notifications_update != self.version:
            try:
                await self.cbpi.config.add(self.name+"_update", self.version, type=ConfigType.STRING, description="Mail Notifications Update Version",source="hidden")
            except Exception as e:
                logger.warning('Unable to update config')
                logger.error(e)



    async def messageEvent(self, cbpi, title, message, type, action):

            if smtp_address is None or smtp_address == "":
                return

            if smtp_port is None or  smtp_port == "":
                return

            if smtp_user is None or smtp_user == "":
                return

            if smtp_pass is None or smtp_pass == "":
                return

            if smtp_encryption is None or smtp_encryption == "":
                return


            # Create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = smtp_user
            message["To"] = "max@bryggmasarna.se"
            message["Subject"] = title

            message.attach(MIMEText(message, "plain"))

            # Create a secure SSL context
            context = ssl.create_default_context()
            server = None

            if smtp_encryption == "SSL":
                server = smtplib.SMTP_SSL(smtp_address, smtp_port, context=context)

            elif smtp_encryption == "TLS":
                server = smtplib.SMTP(smtp_address, smtp_port)
                try:
                    server.starttls(context=context)
                except Exception as e:
                    # Print any error messages to stdout
                    print(e)

            if server != None:
                try:
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, "max@bryggmasarna.se", message.as_string())
                except Exception as e:
                    # Print any error messages to stdout
                    print(e)

                server.quit()


def setup(cbpi):
    cbpi.plugin.register("PushOver", PushOver)
    pass
