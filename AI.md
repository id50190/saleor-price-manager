# AI Instructions

Hello AI! 👋

Please, do not modify this file!

This repository is a eCommerce web application built with SvelteKit 5 and TailwindCSS based on Saleor API, FastAPI.

## Rules

- Don’t care about old versions of Node. Need support only Node 22.x (LTS) for [Vercel](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions) and Node 24.7.0 ([latest](https://nodejs.org/en/download/current)).
- We currently do not support Windows or macOS. Only Ubuntu in the latest LTS version.
- Use `pnpm` as a package manager, but `npm` should be supported too.
- Packages `dotenv` and `dotenv-cli` should not be in the project. We should manage environment variables "manually" via shell. Environment variables should be stored in `.env`-type files.

## Style

- Prefer async/await over Promises.
- Always use TypeScript strict mode.
- Use two spaces for indentation.
- Use one space to indent code before an inline comment.
