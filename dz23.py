from random import randint as ran, shuffle
import asyncio
import logging
import sys
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext


API_TOKEN ='5485255207:AAEPMHtr1dJPAz82t1EYeNbl8-hicVG7yOU'
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storege = MemoryStorage()
dp = Dispatcher(bot, storage=storege)

class Form_Answers(StatesGroup):
    started = State()
    question_state = State()
    game = State()
    end = State()


start_kb = types.InlineKeyboardMarkup()
start_kb.add(types.InlineKeyboardButton('Начать',callback_data='Начать'))
start_kb.add(types.InlineKeyboardButton('Правила',callback_data='Правила'))

rules_kb = types.InlineKeyboardMarkup()
rules_kb.add(types.InlineKeyboardButton('Начать',callback_data='Начать'))

next_kb = types.InlineKeyboardMarkup()
next_kb.add(types.InlineKeyboardButton('Далее',callback_data= 'Далее'))
next_kb.add(types.InlineKeyboardButton('Стоп',callback_data='Стоп'))

@dp.message_handler(commands=['start'],state='*')
async def starting_bot(message: types.Message, state: FSMContext):
        await state.finish()
        await message.reply('Привет! Я бот для работы с вопросами. Вы можете начать игру с помощью /start',reply_markup=start_kb)
        await Form_Answers.started.set()



@dp.callback_query_handler(state=Form_Answers.started)
async def starting_bot(query: types.CallbackQuery, state: FSMContext):    
    if query.data == 'Начать':
        await state.update_data(correct=0)
        await state.update_data(wrong=0)
        await state.update_data(game=0)
        znaks = ['+', '-', '/','*']
        question = str(ran(1,100)) + znaks[ran(0,3)] + str(ran(1,100))
        answers_kb = types.InlineKeyboardMarkup()
        answers_kb.add(types.InlineKeyboardButton(question,callback_data='correct'))
        for i in range(3):
            question_variant = str(ran(1,100)) + znaks[ran(0,3)] + str(ran(1,100))
            answers_kb.add(types.InlineKeyboardButton(question_variant,callback_data='not'))
        shuffle(answers_kb['inline_keyboard'])

        await state.update_data(question_state=eval(question))
        await query.message.edit_text(eval(question),reply_markup=answers_kb)
        await Form_Answers.question_state.set()

    elif query.data == 'Правила':
            await query.message.edit_text('Правила:\n Бот даёт решение из доступных действий(+,-,*,/)', reply_markup=start_kb)

@dp.callback_query_handler(state=Form_Answers.question_state)
async def is_correct(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy( ) as data:
        answer = data['question_state']
        data['game']+=1
        if query.data == 'correct':
                text = 'Правильно!'
                data['correct']+=1
        else:
             text = 'Неправильно!'
             data['wrong']+=1
        await query.message.edit_text(text,reply_markup=next_kb)
        await Form_Answers.game.set()

@dp.callback_query_handler(state=Form_Answers.game)
async def is_stopgame(query: types.CallbackQuery, state: FSMContext):
        if query.data == 'Стоп':
              await query.message.reply('Окей, заканчиваю игру', reply_markup=types.ReplyKeyboardRemove())
              await asyncio.sleep(2)
              await query.message.answer('Напиши что угодно для результата')
              await Form_Answers.end.set()
        else:
            znaks = ['*','-','/','+']
            question = str(ran(1,100)) + znaks[ran(0,3)] + str(ran(1,100))
            answers_kb = types.InlineKeyboardMarkup()
            answers_kb.add(types.InlineKeyboardButton(question,callback_data='correct'))
            for i in range(3):
                question_variant = str(ran(1,100)) + znaks[ran(0,3)] + str(ran(1,100))
                answers_kb.add(types.InlineKeyboardButton(question_variant,callback_data='not'))
            shuffle(answers_kb['inline_keyboard'])


            await state.update_data(question_state=eval(question))
            await query.message.edit_text(eval(question),reply_markup=answers_kb)
            await Form_Answers.question_state.set()

@dp.message_handler(state=Form_Answers.end)
async def game_results(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            yes = data['correct']
            no = data['wrong']
            all_answers = data['game']
            await message.answer(f'Твой результат:\n Всего ответов: {all_answers} \n Всего правильных ответов: {yes } \n Всего не правильных {no}' )
            time.sleep(1.5)

            if int(yes) > int(no):
                    await message.answer('У тебя много правильных правильных ответов 😘')
            elif int(yes) < int(no):
                  await message.answer('У тебя много не правильных ответов 😢')
            else:
                  await message.answer('У тебе нет правильных ответов')

            await Form_Answers.started.set()
            time.sleep(3.0)
            await message.answer('Нажми "Начать " для новой игры',reply_markup=start_kb)


@dp.message_handler(state='*')
async def game_result(message: types.Message, state: FSMContext):
      await message.delete()

@dp.callback_query_handler(state='*')
async def is_stopgame(query: types.CallbackQuery, state:FSMContext):
      await query.message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)