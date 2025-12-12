#!/usr/bin/env python3
"""Voice assistant entity integration example. Bare minimum of an integration driver."""
import asyncio
import logging
from asyncio import sleep
from typing import Any

import ucapi
from ucapi import (
    AssistantError,
    AssistantErrorCode,
    AssistantEvent,
    AssistantEventType,
    VoiceAssistant,
)
from ucapi.api_definitions import AssistantSttResponse, AssistantTextResponse
from ucapi.voice_assistant import Attributes as VAAttr
from ucapi.voice_assistant import (
    AudioConfiguration,
)
from ucapi.voice_assistant import Commands as VACommands
from ucapi.voice_assistant import Features as VAFeatures
from ucapi.voice_assistant import (
    SampleFormat,
    VoiceAssistantEntityOptions,
)
from ucapi.voice_stream import VoiceEndReason, VoiceSessionClosed

loop = asyncio.new_event_loop()
api = ucapi.IntegrationAPI(loop)

session_id = 0


@api.listens_to(ucapi.Events.CONNECT)
async def on_connect() -> None:
    # When the remote connects, we just set the device state. We are ready all the time!
    await api.set_device_state(ucapi.DeviceStates.CONNECTED)


@api.listens_to(ucapi.Events.SUBSCRIBE_ENTITIES)
async def on_subscribe_entities(entity_ids: list[str]) -> None:
    for entity_id in entity_ids:
        api.configured_entities.update_attributes(entity_id, {VAAttr.STATE: "ON"})


async def on_voice_cmd(
    entity: ucapi.VoiceAssistant, cmd_id: str, params: dict[str, Any] | None
) -> ucapi.StatusCodes:
    """
    Voice assistant command handler.

    Called by the integration-API if a command is sent to a configured voice_assistant-entity.

    :param entity: voice assistant entity
    :param cmd_id: command
    :param params: optional command parameters
    :return: status of the command
    """
    # HACK until core is fixed
    global session_id

    print(f"Got {entity.id} command request: {cmd_id} {params}")
    if params is None:
        return ucapi.StatusCodes.BAD_REQUEST

    session_id = params.get("session_id", 0)
    if session_id <= 0:
        return ucapi.StatusCodes.BAD_REQUEST

    if cmd_id == VACommands.VOICE_START:
        ready_evt = AssistantEvent(
            type=AssistantEventType.READY,
            entity_id=entity.id,
            session_id=session_id,
        )
        await api.broadcast_assistant_event(ready_evt)

        # Acknowledge start; binary audio will arrive on the WS binary channel
        return ucapi.StatusCodes.OK
    return ucapi.StatusCodes.NOT_IMPLEMENTED


async def on_voice_session(session):
    print(
        f"Voice stream started: session={session.session_id}, "
        f"{session.config.channels}ch @ {session.config.sample_rate} Hz {session.config.sample_format.value}"
    )
    # HACK until core is fixed
    global session_id

    total = 0
    try:
        async for frame in session:  # frame is bytes
            total += len(frame)
            # feed frame into your voice assistant / LLM here
            print(f"Got {len(frame)} bytes of audio data")
        print(f"Voice stream ended: session={session.session_id}, bytes={total}")

        event = AssistantEvent(
            type=AssistantEventType.STT_RESPONSE,
            entity_id=session.entity_id,
            session_id=session_id,
            data=AssistantSttResponse(
                text="I'm just a demo and I don't know what you said."
            ),
        )
        await session.send_event(event)

        await sleep(1)
        event = AssistantEvent(
            type=AssistantEventType.TEXT_RESPONSE,
            entity_id=session.entity_id,
            session_id=session_id,
            data=AssistantTextResponse(
                success=True, text=f"You have sent {total} bytes of audio data"
            ),
        )
        await session.send_event(event)

        await sleep(1)
    except VoiceSessionClosed as ex:
        print(
            f"Voice stream session {session.session_id} closed (bytes={total})! Reason: {ex.reason}, exception: {ex.error}"
        )
        if ex.reason == VoiceEndReason.REMOTE:
            return  # Remote disconnected
        event = AssistantEvent(
            type=AssistantEventType.ERROR,
            entity_id=session.entity_id,
            session_id=session_id,
            data=AssistantError(
                code=(
                    AssistantErrorCode.TIMEOUT
                    if ex.reason == VoiceEndReason.TIMEOUT
                    else AssistantErrorCode.UNEXPECTED_ERROR
                ),
                message=f"Reason: {ex.reason}, exception: {ex.error}",
            ),
        )
        await session.send_event(event)

    # final event
    event = AssistantEvent(
        type=AssistantEventType.FINISHED,
        entity_id=session.entity_id,
        session_id=session_id,
    )
    await session.send_event(event)


if __name__ == "__main__":
    logging.basicConfig()

    entity = VoiceAssistant(
        identifier="va_main",
        name={"en": "Demo Voice Assistant"},
        features=[VAFeatures.TRANSCRIPTION, VAFeatures.RESPONSE_TEXT],
        attributes={VAAttr.STATE.value: "ON"},
        options=VoiceAssistantEntityOptions(
            audio_cfg=AudioConfiguration(
                channels=1, sample_rate=16000, sample_format=SampleFormat.I16
            ),
        ),
        cmd_handler=on_voice_cmd,
    )

    api.available_entities.add(entity)
    api.set_voice_stream_handler(on_voice_session)

    loop.run_until_complete(api.init("voice.json"))
    loop.run_forever()
