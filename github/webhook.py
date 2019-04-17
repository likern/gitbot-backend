@app.route("/", methods=['POST'])
async def github(request):
    update = Update.parse_obj(request.json)

    result = await db.updates.update_one(
        {"update_id": update.update_id},
        {"$setOnInsert": update.dict(skip_defaults=True)},
        upsert=True
    )
    print(f"[MONGODB] [Update] was added [{result.acknowledged}]")

    status = None
    if result.acknowledged:
        status = 200
    else:
        status = 502

    # Schedule to process telegram update
    # app.add_task(process_text_message(update.message.dict(skip_defaults=True)))
    app.add_task(process_text_message(update.message))
    app.add_task(create_if_new_user(update.message.sender))

    return json({}, status=status)
