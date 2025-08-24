# **YouTube Transcriber with LLM Formatting: Product Requirements Document**

## **1. Vision \& Goal**

**Project Name:** Verbatim AI
**Project Author:** Darko Kuzmanovic
**Vision:** To create a simple, web-based tool that allows users to quickly get a raw transcript from a YouTube video and then use a Large Language Model (LLM) to format it into a clean, readable, and summarized document.
**Goal:** This project aims to provide a user-friendly interface for transcribing YouTube videos and leveraging the power of LLMs to make the transcript more useful. This will be a valuable tool for students, researchers, content creators, and anyone who needs to quickly extract and understand the content of a video.

## **2. Target Audience**

- **Students:** To quickly get notes and summaries from educational videos.
- **Researchers:** To easily analyze the content of interviews, lectures, and documentaries.
- **Content Creators:** To repurpose video content into blog posts, articles, or social media updates.
- **Journalists:** To quickly transcribe interviews and press conferences.
- **General Users:** Anyone who wants to get the text version of a video for easier reading, searching, or sharing.

## **3. Core Features \& Functionality**

### **3.1. YouTube Video Input**

- The user will be able to paste a YouTube video URL into an input field.
- The application will extract the video ID from the URL.

### **3.2. Transcript Fetching**

- The application will use the youtube-transcript-api to fetch the raw transcript of the video.
- The raw transcript will be displayed in a designated area of the UI.
- A "Copy to Clipboard" button will be available for the raw transcript.

### **3.3. LLM Formatting**

- The user will have a button to "Format with AI".
- When clicked, the raw transcript will be sent to the OpenRouter API.
- The application will use a pre-defined prompt to instruct the LLM on how to format the text.

### **3.4. Formatted Transcript Display**

- The formatted transcript from the OpenRouter API will be displayed in a separate area of the UI.
- The formatted text should be easy to read, with clear headings, paragraphs, and bullet points where appropriate.
- A "Copy to Clipboard" button will be available for the formatted transcript.

## **4. User Interface (UI) \& User Experience (UX) Flow**

The UI should be clean, simple, and intuitive.

1. **Initial State:** The user is presented with a clean interface containing:

   - A prominent input field for the YouTube URL.
   - A "Get Transcript" button.

2. **Fetching Transcript:**

   - The user pastes a YouTube URL and clicks "Get Transcript".
   - A loading indicator is displayed while the transcript is being fetched.

3. **Displaying Raw Transcript:**

   - The raw transcript appears in a text area on the left side of the screen.
   - The "Format with AI" button becomes active.

4. **Formatting with AI:**

   - The user clicks "Format with AI".
   - A loading indicator is displayed over the formatted text area.

5. **Displaying Formatted Transcript:**

   - The formatted transcript appears in a text area on the right side of the screen.
   - Both text areas have "Copy to Clipboard" buttons.

## **5. Technical Stack**

- **Frontend:**

  - HTML5
  - CSS3 (with a framework like Tailwind CSS for styling)
  - JavaScript (to handle user interactions and API calls)

- **Backend:**

  - Python with a web framework like **Flask** or **FastAPI** to serve the frontend and interact with the youtube-transcript-api.

- **APIs:**

  - **youtube-transcript-api:** The Python library for getting YouTube transcripts.
  - **OpenRouter API:** For accessing various LLMs for text formatting.

## **6. LLM Formatting Prompt**

This is the core prompt that will be sent to the OpenRouter API along with the raw transcript.

```nocode
You are an expert in text formatting and summarization. Your task is to take the raw, unformatted transcript provided below and transform it into a clean, readable, and well-structured document.

\*\*Instructions:\*\*

1\.  \*\*Add Punctuation and Capitalization:\*\* The transcript is raw text without proper punctuation or capitalization. Add periods, commas, question marks, and capitalize the beginning of sentences and proper nouns.
2.  \*\*Create Paragraphs:\*\* Break the text into logical paragraphs based on the topics being discussed.
3.  \*\*Create a Summary:\*\* At the very top of the document, provide a concise summary of the entire video in 3-5 sentences.
4.  \*\*Identify Key Topics:\*\* After the summary, create a "Key Topics" section with a bulleted list of the main topics discussed in the video.
5.  \*\*Format the Transcript:\*\* After the "Key Topics" section, provide the full, formatted transcript with clear paragraph breaks.
6.  \*\*Use Markdown:\*\* Use Markdown for formatting (e.g., `##` for headings, `\*` for bullet points).

\*\*Raw Transcript:\*\*

{INSERT\_RAW\_TRANSCRIPT\_HERE}

\*\*Output Format:\*\*

\## Summary

{Your 3-5 sentence summary here}

\## Key Topics

\* {Key Topic 1}
\* {Key Topic 2}
\* {Key Topic 3}
\* ...

\## Transcript

{Your fully formatted transcript with paragraphs here}

```

## **7. Error Handling**

The application should gracefully handle the following potential errors:

- **Invalid YouTube URL:** Display a message to the user that the URL is not valid.
- **Transcript Not Available:** If the youtube-transcript-api cannot find a transcript, inform the user.
- **API Errors:** If there is an error with the OpenRouter API, display a generic error message and suggest trying again later.

## **8. Future Enhancements**

- **Language Selection:** Allow the user to select the language of the transcript if multiple languages are available.
- **Different Summary Formats:** Offer different summary lengths or formats (e.g., bullet points, one-paragraph summary).
- **Speaker Diarization:** If possible, identify and label different speakers in the transcript.
- **Export Options:** Allow users to export the formatted transcript as a .txt or .md file.
- **User Accounts:** Allow users to save their transcripts and formatting history.
