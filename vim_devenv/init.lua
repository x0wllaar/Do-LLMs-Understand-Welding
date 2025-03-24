function TableConcat(a, b)
    local nt = {}

    for _,v in ipairs(a) do
   	table.insert(nt, v)
    end
    for _,v in ipairs(b) do
   	table.insert(nt, v)
    end

    return nt
end

require("global.pre_lazy")
require("local.pre_lazy")

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

local local_plugins = require("local.plugins")
local global_plugins = require("global.plugins")
local all_plugins = TableConcat(local_plugins, global_plugins)
require("lazy").setup(all_plugins)

require("local.init")
require("global.init")
